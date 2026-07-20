--!strict
-- Secure, server-authoritative group teleport from the lobby to BunkerGame.
-- Synchronizes with LobbyBuilder via BunkerEvents.LobbyReady.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TeleportService = game:GetService("TeleportService")
local Workspace = game:GetService("Workspace")

local BUNKER_GAME_PLACE_ID = 72688245649120
local PAD_RADIUS = 6
local COOLDOWN_SECONDS = 8
local PAD_NAMES = { "TP1Beacon", "TP2Beacon", "TP3Beacon", "TP4Beacon" }

local remotes = ReplicatedStorage:FindFirstChild("RemoteEvents")
if not remotes then
	remotes = Instance.new("Folder")
	remotes.Name = "RemoteEvents"
	remotes.Parent = ReplicatedStorage
end

local remote = remotes:FindFirstChild("GroupTeleportEvent") :: RemoteEvent?
if not remote then
	remote = Instance.new("RemoteEvent")
	remote.Name = "GroupTeleportEvent"
	remote.Parent = remotes
end

-- Shared event bus for lobby lifecycle
local eventFolder = ReplicatedStorage:FindFirstChild("BunkerEvents")
if not eventFolder then
	eventFolder = Instance.new("Folder")
	eventFolder.Name = "BunkerEvents"
	eventFolder.Parent = ReplicatedStorage
end

local lobbyReadyEvent = eventFolder:FindFirstChild("LobbyReady") :: BindableEvent?
if not lobbyReadyEvent then
	lobbyReadyEvent = Instance.new("BindableEvent")
	lobbyReadyEvent.Name = "LobbyReady"
	lobbyReadyEvent.Parent = eventFolder
end

local pads: { BasePart } = {}
local lastRequest: { [Player]: number } = {}
local lastNotice: { [Player]: number } = {}
local connections: { RBXScriptConnection } = {}

local function clearPads()
	for _, conn in connections do
		conn:Disconnect()
	end
	table.clear(connections)
	table.clear(pads)
end

local function getRoot(player: Player): BasePart?
	local character = player.Character
	if not character then return nil end
	return character:FindFirstChild("HumanoidRootPart") :: BasePart?
end

local function nearestPad(player: Player): BasePart?
	local root = getRoot(player)
	if not root then return nil end

	local best: BasePart? = nil
	local bestDistance = PAD_RADIUS
	for _, pad in pads do
		if pad.Parent then
			local flatDelta = Vector3.new(root.Position.X - pad.Position.X, 0, root.Position.Z - pad.Position.Z)
			local distance = flatDelta.Magnitude
			if distance <= bestDistance and math.abs(root.Position.Y - pad.Position.Y) <= 8 then
				best = pad
				bestDistance = distance
			end
		end
	end
	return best
end

local function playersOnPad(pad: BasePart): { Player }
	local group = {}
	for _, player in Players:GetPlayers() do
		local root = getRoot(player)
		if root then
			local flatDelta = Vector3.new(root.Position.X - pad.Position.X, 0, root.Position.Z - pad.Position.Z)
			if flatDelta.Magnitude <= PAD_RADIUS and math.abs(root.Position.Y - pad.Position.Y) <= 8 then
				table.insert(group, player)
			end
		end
	end
	return group
end

local function notifyPad(player: Player, pad: BasePart)
	local now = os.clock()
	if now - (lastNotice[player] or 0) < 0.5 then return end
	lastNotice[player] = now
	remote:FireClient(player, "PadNearby", {
		padName = pad.Name,
		label = pad:GetAttribute("DisplayName") or "START GAME",
		groupSize = #playersOnPad(pad),
	})
end

local function teleportFromPad(requestingPlayer: Player)
	local now = os.clock()
	if now - (lastRequest[requestingPlayer] or 0) < COOLDOWN_SECONDS then return end

	local pad = nearestPad(requestingPlayer)
	if not pad then
		remote:FireClient(requestingPlayer, "Rejected", "Stand on a launcher pad")
		return
	end

	local group = playersOnPad(pad)
	if #group == 0 or not table.find(group, requestingPlayer) then
		remote:FireClient(requestingPlayer, "Rejected", "No players detected on this pad")
		return
	end

	lastRequest[requestingPlayer] = now
	for _, player in group do
		remote:FireClient(player, "Teleporting", #group)
	end

	if RunService:IsStudio() then
		warn(string.format("[TeleportHandler] Studio preview: would teleport %d player(s) to %d", #group, BUNKER_GAME_PLACE_ID))
		for _, player in group do
			remote:FireClient(player, "StudioPreview", BUNKER_GAME_PLACE_ID)
		end
		return
	end

	local options = Instance.new("TeleportOptions")
	options:SetTeleportData({ source = "BunkerLobby", pad = pad.Name })
	local ok, teleportError = pcall(function()
		TeleportService:TeleportAsync(BUNKER_GAME_PLACE_ID, group, options)
	end)
	if not ok then
		warn("[TeleportHandler] TeleportAsync failed: " .. tostring(teleportError))
		for _, player in group do
			remote:FireClient(player, "Rejected", "Teleport failed. Try again.")
		end
	end
end

local function registerPad(name: string)
	local lobby = Workspace:FindFirstChild("BunkerLobby")
	if not lobby then return false end
	local found = lobby:FindFirstChild(name)
	if not found or not found:IsA("BasePart") then
		warn("[TeleportHandler] Missing launcher trigger: " .. name)
		return false
	end

	found.CanTouch = true
	local touchConn = found.Touched:Connect(function(hit)
		local character = hit:FindFirstAncestorOfClass("Model")
		local player = character and Players:GetPlayerFromCharacter(character)
		if player then notifyPad(player, found) end
	end)
	table.insert(connections, touchConn)

	local prompt = found:FindFirstChildOfClass("ProximityPrompt")
	if prompt then
		local promptConn = prompt.Triggered:Connect(teleportFromPad)
		table.insert(connections, promptConn)
	end

	table.insert(pads, found)
	return true
end

local function registerAllPads()
	clearPads()
	local count = 0
	for _, padName in PAD_NAMES do
		if registerPad(padName) then count += 1 end
	end
	return count
end

-- Initial registration
local initialCount = registerAllPads()
print(string.format("[TeleportHandler] Initial registration: %d pads found", initialCount))

-- Re-register whenever LobbyBuilder signals the lobby is rebuilt
lobbyReadyEvent.Event:Connect(registerAllPads)

remote.OnServerEvent:Connect(function(player, action)
	if action == "TeleportNow" then teleportFromPad(player) end
end)

Players.PlayerRemoving:Connect(function(player)
	lastRequest[player] = nil
	lastNotice[player] = nil
end)

print(string.format("[TeleportHandler] Ready — waiting for BunkerLobby pads"))
