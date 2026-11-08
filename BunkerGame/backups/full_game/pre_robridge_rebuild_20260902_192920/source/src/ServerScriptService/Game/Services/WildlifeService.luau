--!strict
--[[
	WildlifeService — CP06 ambient wildlife

	Server-authoritative, low-cost ambient wildlife:
	- 3-5 distant deer-like silhouettes in forest perimeters
	- 2-3 bird silhouettes traversing overhead
	- Deterministic waypoints, slow wander, no per-frame AI
	- Tick rate: ~3 seconds via task.delay loop
	- All runtime clones cleaned up on Stop()

	Anchors live in GameWorld.Exterior.Wildlife (filesystem source of truth).
	Models are instantiated at runtime under Workspace.Runtime.Wildlife.
--]]

local TweenService = game:GetService("TweenService")

-- ── Tuning ───────────────────────────────────────────────────────────
local TICK_INTERVAL = 3.0          -- seconds between wander updates
local DEER_WALK_SPEED = 5          -- studs/sec tween speed
local BIRD_WALK_SPEED = 18         -- studs/sec for bird traversal
local BIRD_PERIOD = 45             -- seconds between bird crossings
local BIRD_ALTITUDE = 75           -- Y position for birds
local GROUND_Y = 54.0              -- DatumY

-- ── Deterministic waypoint sets (fixed, no RNG) ──────────────────────
-- West forest zone: X -140 to -195, Z 0-140
local DEER_WAYPOINTS: { { x: number, z: number } } = {
	-- West forest herd (3 deer)
	{ x = -155, z = 25 },
	{ x = -170, z = 55 },
	{ x = -185, z = 85 },
	{ x = -165, z = 110 },
	{ x = -148, z = 70 },
	-- East forest herd (2 deer)
	{ x = 175, z = -15 },
	{ x = 195, z = 15 },
	{ x = 210, z = 45 },
	{ x = 185, z = 60 },
	{ x = 200, z = -10 },
}

-- Each deer gets a deterministic start index (cycles through its zone waypoints)
local DEER_START_INDICES = { 1, 3, 5, 7, 9 } -- 5 deer total

-- Bird crossing paths: fixed start/end at high altitude
local BIRD_PATHS: { { sx: number, sz: number, ex: number, ez: number } } = {
	{ sx = -200, sz = -40, ex = 200, ez = 100 },
	{ sx = 180, sz = 120, ex = -180, ez = -20 },
	{ sx = -100, sz = 140, ex = 160, ez = -30 },
}

-- ── Earth tones for deer ─────────────────────────────────────────────
local DEER_COLORS = {
	body  = Color3.fromRGB(101, 78, 56),
	head  = Color3.fromRGB(115, 88, 62),
	legs  = Color3.fromRGB(80, 60, 42),
}

-- ── Service ──────────────────────────────────────────────────────────
local WildlifeService = {}
WildlifeService.__index = WildlifeService

function WildlifeService.new()
	return setmetatable({
		_initialized = false,
		_started = false,
		_runtimeFolder = nil :: Folder?,
		_deer = {} :: { model: Model, waypointIndex: number, zoneOffset: number },
		_birds = {} :: { part: Part, pathIndex: number, nextCrossingAt: number },
		_tickConnection = nil,
		_birdConnections = {} :: { RBXScriptConnection },
	}, WildlifeService)
end

function WildlifeService.Init(self, bag)
	if self._initialized then
		return
	end
	self._initialized = true
end

-- ── Deer model builder ───────────────────────────────────────────────
local function buildDeerModel(name: string): Model
	local model = Instance.new("Model")
	model.Name = name

	-- Body (PrimaryPart)
	local body = Instance.new("Part")
	body.Name = "Body"
	body.Size = Vector3.new(3, 1.5, 2)
	body.Color = DEER_COLORS.body
	body.Material = Enum.Material.SmoothPlastic
	body.Anchored = true
	body.CanCollide = false
	body.CastShadow = true
	body.TopSurface = Enum.SurfaceType.Smooth
	body.BottomSurface = Enum.SurfaceType.Smooth
	body.Parent = model

	-- Head
	local head = Instance.new("Part")
	head.Name = "Head"
	head.Size = Vector3.new(1, 1, 1)
	head.Color = DEER_COLORS.head
	head.Material = Enum.Material.SmoothPlastic
	head.Anchored = true
	head.CanCollide = false
	head.CastShadow = true
	head.TopSurface = Enum.SurfaceType.Smooth
	head.BottomSurface = Enum.SurfaceType.Smooth
	head.CFrame = CFrame.new(0, 0.5, -1.8) -- forward from body
	head.Parent = model

	-- Neck (connecting body to head)
	local neck = Instance.new("Part")
	neck.Name = "Neck"
	neck.Size = Vector3.new(0.5, 1.2, 0.6)
	neck.Color = DEER_COLORS.body
	neck.Material = Enum.Material.SmoothPlastic
	neck.Anchored = true
	neck.CanCollide = false
	neck.CastShadow = false
	neck.Transparency = 0.0
	neck.TopSurface = Enum.SurfaceType.Smooth
	neck.BottomSurface = Enum.SurfaceType.Smooth
	neck.CFrame = CFrame.new(0, 0.6, -1.2)
	neck.Parent = model

	-- 4 Legs
	local legPositions = {
		{ name = "FrontLeft",  offset = Vector3.new(-0.8, -0.75, -0.8) },
		{ name = "FrontRight", offset = Vector3.new(0.8, -0.75, -0.8) },
		{ name = "RearLeft",   offset = Vector3.new(-0.8, -0.75, 0.8) },
		{ name = "RearRight",  offset = Vector3.new(0.8, -0.75, 0.8) },
	}
	for _, leg in ipairs(legPositions) do
		local part = Instance.new("Part")
		part.Name = leg.name
		part.Size = Vector3.new(0.3, 1.0, 0.3)
		part.Color = DEER_COLORS.legs
		part.Material = Enum.Material.SmoothPlastic
		part.Anchored = true
		part.CanCollide = false
		part.CastShadow = false
		part.TopSurface = Enum.SurfaceType.Smooth
		part.BottomSurface = Enum.SurfaceType.Smooth
		part.CFrame = CFrame.new(leg.offset)
		part.Parent = model
	end

	model.PrimaryPart = body
	return model
end

-- ── Bird part builder ────────────────────────────────────────────────
local function buildBirdPart(name: string): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Size = Vector3.new(0.5, 0.15, 0.5)
	part.Color = Color3.fromRGB(35, 30, 28)
	part.Material = Enum.Material.SmoothPlastic
	part.Anchored = true
	part.CanCollide = false
	part.CastShadow = false
	part.Transparency = 0.35
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	return part
end

-- ── Spawn wildlife ───────────────────────────────────────────────────
function WildlifeService:_spawnDeer()
	-- Find anchor positions from GameWorld or use hardcoded defaults
	local anchorFolder = self:_findAnchorFolder()

	for i, startIndex in ipairs(DEER_START_INDICES) do
		local deer = buildDeerModel("Deer" .. i)
		-- Determine which zone this deer belongs to
		local zoneOffset = (i <= 3) and 0 or 5
		local wpIndex = startIndex
		local wp = DEER_WAYPOINTS[wpIndex]
		local spawnCFrame = CFrame.new(wp.x, GROUND_Y + 0.75, wp.z)
		-- Orient to face next waypoint
		local nextWpIndex = (wpIndex % #DEER_WAYPOINTS) + 1
		local nextWp = DEER_WAYPOINTS[nextWpIndex]
		local dir = Vector3.new(nextWp.x - wp.x, 0, nextWp.z - wp.z).Unit
		deer:SetPrimaryPartCFrame(spawnCFrame * CFrame.Angles(0, math.atan2(dir.X, dir.Z), 0))
		deer.Parent = self._runtimeFolder

		table.insert(self._deer, {
			model = deer,
			waypointIndex = wpIndex,
			zoneOffset = zoneOffset,
		})
	end
end

function WildlifeService:_spawnBirds()
	for i, path in ipairs(BIRD_PATHS) do
		local bird = buildBirdPart("Bird" .. i)
		-- Start at the start point, hidden
		bird.CFrame = CFrame.new(path.sx, BIRD_ALTITUDE, path.sz)
		bird.Parent = self._runtimeFolder

		table.insert(self._birds, {
			part = bird,
			pathIndex = i,
			nextCrossingAt = os.clock() + (i * 5), -- stagger initial crossings
		})
	end
end

-- ── Movement tick ────────────────────────────────────────────────────
function WildlifeService:_tickDeer()
	for _, entry in ipairs(self._deer) do
		local wpIndex = entry.waypointIndex
		local wp = DEER_WAYPOINTS[wpIndex]
		local nextIndex = (wpIndex % #DEER_WAYPOINTS) + 1
		local nextWp = DEER_WAYPOINTS[nextIndex]

		-- Calculate direction and tween
		local fromPos = Vector3.new(wp.x, GROUND_Y + 0.75, wp.z)
		local toPos = Vector3.new(nextWp.x, GROUND_Y + 0.75, nextWp.z)
		local distance = (toPos - fromPos).Magnitude
		local duration = distance / DEER_WALK_SPEED

		-- Face direction of travel
		local dir = (toPos - fromPos).Unit
		local angle = math.atan2(dir.X, dir.Z)
		local targetCFrame = CFrame.new(toPos) * CFrame.Angles(0, angle, 0)

		local model = entry.model
		local primaryPart = model.PrimaryPart
		if primaryPart and primaryPart.Parent then
			local tweenInfo = TweenInfo.new(duration, Enum.EasingStyle.Linear, Enum.EasingDirection.InOut)
			local tween = TweenService:Create(primaryPart, tweenInfo, { CFrame = targetCFrame })
			tween:Play()
		end

		-- Advance waypoint
		entry.waypointIndex = nextIndex
	end
end

function WildlifeService:_tickBirds()
	local now = os.clock()
	for _, entry in ipairs(self._birds) do
		if now >= entry.nextCrossingAt then
			local path = BIRD_PATHS[entry.pathIndex]
			local fromPos = Vector3.new(path.sx, BIRD_ALTITUDE, path.sz)
			local toPos = Vector3.new(path.ex, BIRD_ALTITUDE, path.ez)
			local distance = (toPos - fromPos).Magnitude
			local duration = distance / BIRD_WALK_SPEED

			local part = entry.part
			if part and part.Parent then
				part.CFrame = CFrame.new(fromPos)
				local tweenInfo = TweenInfo.new(duration, Enum.EasingStyle.Linear, Enum.EasingDirection.InOut)
				local tween = TweenService:Create(part, tweenInfo, { CFrame = CFrame.new(toPos) })
				tween:Play()
			end

			entry.nextCrossingAt = now + BIRD_PERIOD
			-- Alternate direction next time
			local temp = BIRD_PATHS[entry.pathIndex].sx
			BIRD_PATHS[entry.pathIndex].sx = BIRD_PATHS[entry.pathIndex].ex
			BIRD_PATHS[entry.pathIndex].ex = temp
			temp = BIRD_PATHS[entry.pathIndex].sz
			BIRD_PATHS[entry.pathIndex].sz = BIRD_PATHS[entry.pathIndex].ez
			BIRD_PATHS[entry.pathIndex].ez = temp
		end
	end
end

function WildlifeService:_tick()
	if not self._started then
		return
	end
	self:_tickDeer()
	self:_tickBirds()
	-- Schedule next tick
	task.delay(TICK_INTERVAL, function()
		self:_tick()
	end)
end

-- ── Anchor finder ────────────────────────────────────────────────────
function WildlifeService:_findAnchorFolder(): Folder?
	-- Try to find the Wildlife anchors in GameWorld.Exterior.Wildlife
	local gameWorld = workspace:FindFirstChild("GameWorld")
	if gameWorld then
		local exterior = gameWorld:FindFirstChild("Exterior")
		if exterior then
			local wildlife = exterior:FindFirstChild("Wildlife")
			if wildlife and wildlife:IsA("Folder") then
				return wildlife
			end
		end
	end
	return nil
end

-- ── Lifecycle ────────────────────────────────────────────────────────
function WildlifeService.Start(self)
	if self._started then
		return
	end
	assert(self._initialized, "WildlifeService must initialize before Start")
	self._started = true

	-- Create runtime folder
	local runtime = workspace:FindFirstChild("Runtime")
	if not runtime then
		runtime = Instance.new("Folder")
		runtime.Name = "Runtime"
		runtime.Parent = workspace
	end
	local wildlifeFolder = Instance.new("Folder")
	wildlifeFolder.Name = "Wildlife"
	wildlifeFolder.Parent = runtime
	self._runtimeFolder = wildlifeFolder

	-- Spawn deer and birds
	self:_spawnDeer()
	self:_spawnBirds()

	-- Start movement loop (first tick after a short delay)
	task.delay(1.0, function()
		self:_tick()
	end)
end

function WildlifeService.Stop(self)
	if not self._started then
		return
	end
	self._started = false

	-- Destroy all runtime clones
	if self._runtimeFolder then
		for _, entry in ipairs(self._deer) do
			if entry.model and entry.model.Parent then
				entry.model:Destroy()
			end
		end
		for _, entry in ipairs(self._birds) do
			if entry.part and entry.part.Parent then
				entry.part:Destroy()
			end
		end
		if self._runtimeFolder.Parent then
			self._runtimeFolder:Destroy()
		end
		self._runtimeFolder = nil
	end

	self._deer = {}
	self._birds = {}
end

-- ── Query API (optional, kept minimal) ───────────────────────────────
function WildlifeService:GetWildlife()
	local result = {}
	for _, entry in ipairs(self._deer) do
		local primaryPart = entry.model and entry.model.PrimaryPart
		if primaryPart and primaryPart.Parent then
			table.insert(result, {
				Name = entry.model.Name,
				Position = primaryPart.Position,
			})
		end
	end
	return result
end

return WildlifeService
