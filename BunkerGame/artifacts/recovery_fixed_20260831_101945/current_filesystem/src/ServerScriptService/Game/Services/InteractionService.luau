--!strict

local HttpService = game:GetService("HttpService")
local Config = require(game:GetService("ReplicatedStorage"):WaitForChild("Game"):WaitForChild("Config"))

local TOKEN_SECONDS = Config.Network.InteractionTokenLifetimeSeconds
local MAX_DISTANCE = Config.Network.InteractionMaximumDistance

local ACTIONS_BY_KIND = {
	farm_plot = { "FarmHarvest", "FarmPlant" },
	food_processor = { "ProcessorStart" },
	shop = { "ShopBuy" },
	storage = { "StorageTransfer" },
	power = { "PowerActivate" },
	scrap_exchange = { "ScrapExchange" },
	upgrade = { "UpgradeBuy" },
}

local INTENT_KIND_TO_INTERACTION_KIND = {
	FarmPlant = "farm_plot",
	FarmHarvest = "farm_plot",
	ProcessorStart = "food_processor",
	ShopBuy = "shop",
	StorageTransfer = "storage",
	PowerActivate = "power",
	ScrapExchange = "scrap_exchange",
	UpgradeBuy = "upgrade",
}

local InteractionService = {}
InteractionService.__index = InteractionService

local function livingRoot(player: Player): (Model?, BasePart?)
	local character = player.Character
	if character == nil then
		return nil, nil
	end
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	local root = character:FindFirstChild("HumanoidRootPart")
	if humanoid == nil or humanoid.Health <= 0 or root == nil or not root:IsA("BasePart") then
		return character, nil
	end
	return character, root
end

local function visible(character: Model, target: Instance, origin: Vector3, destination: Vector3): boolean
	local parameters = RaycastParams.new()
	parameters.FilterType = Enum.RaycastFilterType.Exclude
	parameters.FilterDescendantsInstances = { character }
	parameters.IgnoreWater = true
	local result = workspace:Raycast(origin, destination - origin, parameters)
	return result == nil or result.Instance:IsDescendantOf(target)
end

function InteractionService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_world = nil,
		_playerData = nil,
		_inventory = nil,
		_farming = nil,
		_economy = nil,
		_bunker = nil,
		_events = nil,
		_definitions = nil,
		_sessionsByPlayer = {} :: { [Player]: any },
		_sessionsByToken = {} :: { [string]: any },
		_connections = {},
		_sessionGeneration = 0,
	}, InteractionService)
end

function InteractionService.Init(self, bag)
	if self._initialized then
		return
	end
	self._world = bag:Get("WorldService")
	self._playerData = bag:Get("PlayerDataService")
	self._inventory = bag:Get("InventoryService")
	self._farming = bag:Get("FarmingService")
	self._economy = bag:Get("EconomyService")
	self._bunker = bag:Get("BunkerService")
	self._events = bag:Get("DomainEvents")
	self._definitions = bag.Context.Definitions
	self._initialized = true
end

function InteractionService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "InteractionService must initialize before Start")
	self._started = true
	self._sessionGeneration += 1
	local generation = self._sessionGeneration
	for _, interaction in ipairs(self._world:GetInteractions()) do
		table.insert(self._connections, interaction.Prompt.Triggered:Connect(function(player)
			self:HandlePrompt(player, interaction.Id)
		end))
	end
	table.insert(self._connections, self._events:On("CharacterDied", function(player)
		self:InvalidatePlayer(player)
	end))
	task.spawn(function()
		while self._started and self._sessionGeneration == generation do
			for player, session in pairs(self._sessionsByPlayer) do
				local interaction = session.Interaction
				local character, root = livingRoot(player)
				if workspace:GetServerTimeNow() > session.ExpiresAt
					or character == nil
					or root == nil
					or interaction.Instance.Parent == nil
					or interaction.Anchor.Parent == nil
					or (root.Position - interaction.Anchor.Position).Magnitude > MAX_DISTANCE
					or not visible(character, interaction.Instance, root.Position, interaction.Anchor.Position)
				then
					self:InvalidatePlayer(player)
				end
			end
			task.wait(0.25)
		end
	end)
end

function InteractionService:_view(player: Player, interaction)
	local profile = self._playerData:GetView(player)
	assert(profile ~= nil, "interaction view requires a ready profile")
	if interaction.Kind == "farm_plot" then
		return {
			Kind = "farm_plot",
			Plot = self._farming:GetPlotView(interaction.Id, player),
			SeedQuantity = profile.Inventory.seed_wheat or 0,
		}
	elseif interaction.Kind == "food_processor" then
		return {
			Kind = "food_processor",
			IsPowered = self._bunker:IsPowered(),
			CropQuantity = profile.Inventory.crop_wheat or 0,
			Job = self._farming:GetProcessorJobView(player),
		}
	elseif interaction.Kind == "shop" then
		return {
			Kind = "shop",
			Credits = profile.Currencies.credits,
			Offers = self._economy:GetOffersView(),
		}
	elseif interaction.Kind == "storage" then
		return {
			Kind = "storage",
			Inventory = self._inventory:GetItemQuantities(profile.Inventory),
			Storage = self._inventory:GetItemQuantities(profile.Storage),
			StorageUsed = self._inventory:GetStorageUsed(profile),
			StorageCapacity = self._inventory:GetStorageCapacity(profile),
		}
	elseif interaction.Kind == "power" then
		local power = self._bunker:GetView()
		return {
			Kind = "power",
			IsActive = power.IsActive,
			EndsAt = power.EndsAt,
			BatteryQuantity = profile.Inventory.battery_cell or 0,
		}
	elseif interaction.Kind == "scrap_exchange" then
		return {
			Kind = "scrap_exchange",
			ScrapQuantity = profile.Inventory.scrap or 0,
			Credits = profile.Currencies.credits,
			CreditsPerScrap = 5,
		}
	elseif interaction.Kind == "upgrade" then
		local upgradeId = interaction.UpgradeId
		local definition = self._definitions.Upgrades[upgradeId]
		assert(definition ~= nil, string.format("upgrade interaction %s has invalid UpgradeId", interaction.Id))
		return {
			Kind = "upgrade",
			UpgradeId = upgradeId,
			Tier = profile.Upgrades[upgradeId],
			CreditCost = definition.CreditCost,
			Credits = profile.Currencies.credits,
			IsPowered = self._bunker:IsPowered(),
		}
	end
	error(string.format("unknown interaction kind %s", tostring(interaction.Kind)))
end

function InteractionService:HandlePrompt(player: Player, interactionId: string): (boolean, string, any)
	if not self._playerData:IsReady(player) then
		return false, "PROFILE_NOT_READY", nil
	end
	local interaction = self._world:GetInteraction(interactionId)
	if interaction == nil or interaction.Instance.Parent == nil then
		return false, "WRONG_INTERACTION", nil
	end
	local character, root = livingRoot(player)
	if character == nil or root == nil then
		return false, "PLAYER_DEAD", nil
	end
	if (root.Position - interaction.Anchor.Position).Magnitude > MAX_DISTANCE then
		return false, "OUT_OF_RANGE", nil
	end
	if not visible(character, interaction.Instance, root.Position, interaction.Anchor.Position) then
		return false, "LINE_OF_SIGHT_BLOCKED", nil
	end
	self:InvalidatePlayer(player)
	local token = string.lower(HttpService:GenerateGUID(false):gsub("%-", ""))
	local expiresAt = workspace:GetServerTimeNow() + TOKEN_SECONDS
	local session = {
		Player = player,
		Token = token,
		ExpiresAt = expiresAt,
		Interaction = interaction,
	}
	self._sessionsByPlayer[player] = session
	self._sessionsByToken[token] = session
	local actions = table.clone(ACTIONS_BY_KIND[interaction.Kind])
	table.sort(actions)
	local payload = {
		InteractionId = interaction.Id,
		InteractionKind = interaction.Kind,
		Token = token,
		ExpiresAt = expiresAt,
		Actions = actions,
		View = self:_view(player, interaction),
	}
	self._events:Emit("InteractionOpened", player, payload)
	return true, "OK", payload
end

function InteractionService:ValidateToken(player: Player, interactionId: string, token: string, intentKind: string): (boolean, string, any)
	local session = self._sessionsByToken[token]
	if session == nil or session.Player ~= player then
		return false, "INVALID_TOKEN", nil
	end
	if workspace:GetServerTimeNow() > session.ExpiresAt then
		self:InvalidatePlayer(player)
		return false, "TOKEN_EXPIRED", nil
	end
	local interaction = session.Interaction
	if interaction.Id ~= interactionId or INTENT_KIND_TO_INTERACTION_KIND[intentKind] ~= interaction.Kind then
		return false, "WRONG_INTERACTION", nil
	end
	if interaction.Instance.Parent == nil or interaction.Anchor.Parent == nil then
		self:InvalidatePlayer(player)
		return false, "WRONG_INTERACTION", nil
	end
	local character, root = livingRoot(player)
	if character == nil or root == nil then
		self:InvalidatePlayer(player)
		return false, "PLAYER_DEAD", nil
	end
	if (root.Position - interaction.Anchor.Position).Magnitude > MAX_DISTANCE then
		self:InvalidatePlayer(player)
		return false, "OUT_OF_RANGE", nil
	end
	if not visible(character, interaction.Instance, root.Position, interaction.Anchor.Position) then
		self:InvalidatePlayer(player)
		return false, "LINE_OF_SIGHT_BLOCKED", nil
	end
	return true, "OK", interaction
end

function InteractionService:RouteIntent(player: Player, payload): (boolean, string, any)
	local valid, code, interaction = self:ValidateToken(player, payload.InteractionId, payload.Token, payload.Kind)
	if not valid then
		return false, code, nil
	end
	if payload.Kind == "FarmPlant" then
		return self._farming:Plant(player, interaction.Id, payload.CropId)
	elseif payload.Kind == "FarmHarvest" then
		return self._farming:Harvest(player, interaction.Id)
	elseif payload.Kind == "ProcessorStart" then
		return self._farming:StartProcessor(player, payload.RecipeId)
	elseif payload.Kind == "ShopBuy" then
		return self._economy:BuyOffer(player, payload.OfferId, payload.Count)
	elseif payload.Kind == "StorageTransfer" then
		return self._economy:TransferStorage(player, payload.Direction, payload.ItemId, payload.Count)
	elseif payload.Kind == "PowerActivate" then
		return self._bunker:TryActivatePower(player)
	elseif payload.Kind == "ScrapExchange" then
		return self._economy:ExchangeScrap(player, payload.Count)
	elseif payload.Kind == "UpgradeBuy" then
		if interaction.UpgradeId ~= payload.UpgradeId then
			return false, "WRONG_INTERACTION", nil
		end
		return self._economy:BuyUpgrade(player, payload.UpgradeId)
	end
	return false, "UNKNOWN_REQUEST", nil
end

function InteractionService:InvalidatePlayer(player: Player)
	local session = self._sessionsByPlayer[player]
	if session == nil then
		return
	end
	self._sessionsByPlayer[player] = nil
	if self._sessionsByToken[session.Token] == session then
		self._sessionsByToken[session.Token] = nil
	end
end

function InteractionService:CloseSession(player: Player, token: string): boolean
	local session = self._sessionsByPlayer[player]
	if session == nil or session.Token ~= token then
		return false
	end
	self:InvalidatePlayer(player)
	return true
end

function InteractionService.Stop(self)
	if not self._initialized then
		return
	end
	self._started = false
	self._sessionGeneration += 1
	for _, connection in ipairs(self._connections) do
		connection:Disconnect()
	end
	table.clear(self._connections)
	table.clear(self._sessionsByPlayer)
	table.clear(self._sessionsByToken)
end

return InteractionService
