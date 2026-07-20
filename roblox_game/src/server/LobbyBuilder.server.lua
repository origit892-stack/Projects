--!strict
-- LobbyBuilder.server.luau — "THE MAW" v2
-- Dark, cinematic horror cathedral with a central abyss portal,
-- rotating rings, particle columns, and atmosphere that slaps.

local Workspace = game:GetService("Workspace")
local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

-- ============================================================
-- COLORS — high contrast palette
-- ============================================================

local C = {
	abyss       = Color3.fromRGB(8, 4, 18),
	void        = Color3.fromRGB(2, 1, 6),
	stone       = Color3.fromRGB(42, 38, 48),
	stoneLight  = Color3.fromRGB(62, 56, 70),
	stoneDark   = Color3.fromRGB(26, 22, 32),
	obsidian    = Color3.fromRGB(16, 13, 22),
	floor       = Color3.fromRGB(32, 28, 38),
	floorTile   = Color3.fromRGB(46, 40, 52),
	blood       = Color3.fromRGB(170, 14, 20),
	bloodDark   = Color3.fromRGB(80, 8, 12),
	bloodBright = Color3.fromRGB(240, 22, 30),
	ember       = Color3.fromRGB(255, 80, 20),
	emberDim    = Color3.fromRGB(200, 50, 12),
	gold        = Color3.fromRGB(200, 170, 80),
	goldDim     = Color3.fromRGB(130, 110, 52),
	rust        = Color3.fromRGB(100, 48, 28),
	rustDark    = Color3.fromRGB(60, 30, 18),
	iron        = Color3.fromRGB(62, 56, 50),
	ironDark    = Color3.fromRGB(36, 32, 28),
	steel       = Color3.fromRGB(76, 70, 60),
	copper      = Color3.fromRGB(160, 92, 48),
	neonRed     = Color3.fromRGB(255, 22, 28),
	neonRedDim  = Color3.fromRGB(160, 14, 18),
	neonGreen   = Color3.fromRGB(40, 240, 80),
	neonBlue    = Color3.fromRGB(28, 80, 240),
	fluorescent = Color3.fromRGB(210, 216, 226),
	fluorescentDim = Color3.fromRGB(130, 138, 150),
	screen      = Color3.fromRGB(8, 24, 8),
	screenGlow  = Color3.fromRGB(40, 240, 80),
	portal      = Color3.fromRGB(180, 30, 220),
	portalGlow  = Color3.fromRGB(220, 60, 255),
}

-- ============================================================
-- SETUP
-- ============================================================

local previousLobby = Workspace:FindFirstChild("BunkerLobby")
if previousLobby then previousLobby:Destroy() end

local lobbyModel = Instance.new("Model")
lobbyModel.Name = "BunkerLobby"
lobbyModel:SetAttribute("GeneratedBy", "LobbyBuilder")
lobbyModel:SetAttribute("TargetPlaceId", 72688245649120)
lobbyModel.Parent = Workspace

-- Reposition StarterPlayer SpawnLocation for future spawns
local defaultSpawn = game:GetService("StarterPlayer"):FindFirstChild("SpawnLocation")
if defaultSpawn then
	defaultSpawn.Position = Vector3.new(CX, FY + 2, CZ + 20)
	defaultSpawn.Neutral = true
end

print("=== LobbyBuilder STARTED ===")

-- ============================================================
-- PART FACTORIES
-- ============================================================

local partCount = 0

local function pt(name: string, size: Vector3, pos: Vector3, color: Color3, mat: Enum.Material, parent: Instance): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.Size = size
	p.Position = pos
	p.Color = color
	p.Material = mat
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CastShadow = (mat ~= Enum.Material.Neon)
	p.Parent = if parent == Workspace then lobbyModel else parent
	partCount += 1
	return p
end

local function cyl(name: string, diameter: number, height: number, pos: Vector3, color: Color3, mat: Enum.Material, parent: Instance): Part
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.Shape = Enum.PartType.Cylinder
	p.Size = Vector3.new(height, diameter, diameter)
	p.CFrame = CFrame.new(pos) * CFrame.Angles(0, 0, math.rad(90))
	p.Color = color
	p.Material = mat
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CastShadow = (mat ~= Enum.Material.Neon)
	p.Parent = if parent == Workspace then lobbyModel else parent
	partCount += 1
	return p
end

-- ============================================================
-- CONSTANTS
-- ============================================================

local W, D, H = 110, 75, 45
local T = 0.8
local FY = 0.0
local CX, CZ = 0, 0
local HW, HD = W / 2, D / 2
local WY = FY + H / 2
local CY = FY + H
local PIT = 18

-- ============================================================
-- LIGHTING — readable but dramatic
-- ============================================================

Lighting.Ambient = Color3.fromRGB(45, 38, 55)
Lighting.Brightness = 0.3
Lighting.ExposureCompensation = 0.5
Lighting.OutdoorAmbient = Color3.fromRGB(25, 20, 35)
Lighting.ClockTime = 1.5
Lighting.GeographicLatitude = 40
Lighting.FogColor = Color3.fromRGB(25, 20, 32)
Lighting.FogStart = 30
Lighting.FogEnd = 80
Lighting.GlobalShadows = true
Lighting.EnvironmentDiffuseScale = 0.4
Lighting.EnvironmentSpecularScale = 0.2
Lighting.ColorShift_Bottom = Color3.fromRGB(35, 28, 45)
Lighting.ColorShift_Top = Color3.fromRGB(160, 40, 50)

-- ============================================================
-- FLOOR — polished tiles
-- ============================================================

local function buildFloor()
	pt("FloorBase", Vector3.new(W, 0.5, D), Vector3.new(CX, FY - 0.25, CZ), C.abyss, Enum.Material.Concrete, Workspace)
	local TS = 7
	local TH = 0.15
	local nx = math.floor((W - 1) / TS)
	local nz = math.floor((D - 1) / TS)
	local sx = CX - HW + TS / 2
	local sz = CZ - HD + TS / 2
	for ix = 0, nx - 1 do
		for iz = 0, nz - 1 do
			local x = sx + ix * TS
			local z = sz + iz * TS
			if math.abs(x) < PIT + 1 and math.abs(z) < PIT + 1 then continue end
			local checker = (ix + iz) % 2
			local col = if checker == 0 then C.floor else C.floorTile
			pt("Tile_" .. ix .. "_" .. iz, Vector3.new(TS - 0.08, TH, TS - 0.08), Vector3.new(x, FY + TH / 2, z), col, Enum.Material.Slate, Workspace)
		end
	end
end

-- ============================================================
-- THE PIT + PORTAL
-- ============================================================

local pitLights: { PointLight } = {}

local function buildPit()
	for level = 0, 6 do
		local yOff = -level * 2 - 1
		local shrink = level * 0.35
		local half = PIT - shrink
		local col = if level % 2 == 0 then C.stoneDark else C.obsidian
		pt("PW_N_" .. level, Vector3.new(half * 2, 2, 0.6), Vector3.new(CX, FY + yOff, CZ - half), col, Enum.Material.Slate, Workspace)
		pt("PW_S_" .. level, Vector3.new(half * 2, 2, 0.6), Vector3.new(CX, FY + yOff, CZ + half), col, Enum.Material.Slate, Workspace)
		pt("PW_W_" .. level, Vector3.new(0.6, 2, half * 2 - 0.6), Vector3.new(CX - half, FY + yOff, CZ), col, Enum.Material.Slate, Workspace)
		pt("PW_E_" .. level, Vector3.new(0.6, 2, half * 2 - 0.6), Vector3.new(CX + half, FY + yOff, CZ), col, Enum.Material.Slate, Workspace)
	end

	-- Pit floor glow
	pt("PitFloor", Vector3.new(PIT * 2 - 2, 0.4, PIT * 2 - 2), Vector3.new(CX, FY - 15, CZ), C.bloodDark, Enum.Material.CorrodedMetal, Workspace)
	local glowSurf = pt("PitGlow", Vector3.new(PIT * 2 - 6, 0.1, PIT * 2 - 6), Vector3.new(CX, FY - 14.8, CZ), C.neonRed, Enum.Material.Neon, Workspace)
	glowSurf.Transparency = 0.4

	local abyssLight = Instance.new("PointLight")
	abyssLight.Color = C.bloodBright
	abyssLight.Brightness = 8
	abyssLight.Range = 80
	abyssLight.Shadows = true
	abyssLight.Parent = glowSurf
	table.insert(pitLights, abyssLight)

	-- Ghostly portal column — barely visible, just a suggestion
	local portalBeam = pt("PortalBeam", Vector3.new(8, H + 5, 8), Vector3.new(CX, FY + 25, CZ), C.portal, Enum.Material.Glass, Workspace)
	portalBeam.Transparency = 0.85
	portalBeam.Reflectance = 0.1
	portalBeam.CanCollide = false

	-- Faint inner core
	local portalCore = pt("PortalCore", Vector3.new(3, H + 3, 3), Vector3.new(CX, FY + 25, CZ), C.portalGlow, Enum.Material.Glass, Workspace)
	portalCore.Transparency = 0.7
	portalCore.Reflectance = 0.1
	portalCore.CanCollide = false

	-- Portal light
	local portalLight = Instance.new("PointLight")
	portalLight.Color = C.portalGlow
	portalLight.Brightness = 6
	portalLight.Range = 70
	portalLight.Shadows = false
	portalLight.Parent = portalCore

	-- Rotating outer ring
	local ringOuter = cyl("PortalRingOuter", 24, 0.6, Vector3.new(CX, FY + 10, CZ), C.portal, Enum.Material.Neon, Workspace)
	ringOuter.Transparency = 0.3
	local ringOuterLight = Instance.new("PointLight")
	ringOuterLight.Color = C.portalGlow
	ringOuterLight.Brightness = 3
	ringOuterLight.Range = 30
	ringOuterLight.Parent = ringOuter

	local ringInner = cyl("PortalRingInner", 16, 0.4, Vector3.new(CX, FY + 14, CZ), C.portalGlow, Enum.Material.Neon, Workspace)
	ringInner.Transparency = 0.2

	local ringBottom = cyl("PortalRingBot", 20, 0.5, Vector3.new(CX, FY + 2, CZ), C.portalGlow, Enum.Material.Neon, Workspace)
	ringBottom.Transparency = 0.25

	-- Rune symbols floating in the beam
	for i = 0, 5 do
		local angle = math.rad(i * 60)
		local rx = CX + math.cos(angle) * 5
		local rz = CZ + math.sin(angle) * 5
		local rune = pt("Rune_" .. i, Vector3.new(1, 1, 0.1), Vector3.new(rx, FY + 6 + i * 3, rz), C.portalGlow, Enum.Material.Neon, Workspace)
		rune.Transparency = 0.2
		rune.Shape = Enum.PartType.Cylinder
	end
end

-- ============================================================
-- PARTICLES — portal + atmosphere
-- ============================================================

local function buildParticles()
	-- Rising particles in the portal beam
	local pSrc = pt("PSrc", Vector3.new(1, 1, 1), Vector3.new(CX, FY - 10, CZ), C.portal, Enum.Material.SmoothPlastic, Workspace)
	pSrc.Transparency = 1
	local pAtt = Instance.new("Attachment"); pAtt.Parent = pSrc
	local pEm = Instance.new("ParticleEmitter"); pEm.Parent = pAtt
	pEm.Rate = 25
	pEm.Speed = NumberRange.new(4, 10)
	pEm.Lifetime = NumberRange.new(3, 6)
	pEm.SpreadAngle = Vector2.new(8, 8)
	pEm.Acceleration = Vector3.new(0, 5, 0)
	pEm.Texture = "rbxasset://textures/particles/sparkle_02.png"
	pEm.Color = ColorSequence.new({
		ColorSequenceKeypoint.new(0, C.portalGlow),
		ColorSequenceKeypoint.new(0.5, C.portal),
		ColorSequenceKeypoint.new(1, C.bloodBright),
	})
	pEm.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.8),
		NumberSequenceKeypoint.new(0.3, 2),
		NumberSequenceKeypoint.new(1, 0.05),
	})
	pEm.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.8),
		NumberSequenceKeypoint.new(0.2, 0.2),
		NumberSequenceKeypoint.new(1, 1),
	})
	pEm.LightEmission = 1
	pEm.LightInfluence = 0

	-- Orbiting smaller particle ring
	local pRing = pt("PRing", Vector3.new(1, 1, 1), Vector3.new(CX, FY + 12, CZ), C.portal, Enum.Material.SmoothPlastic, Workspace)
	pRing.Transparency = 1
	local pAtt2 = Instance.new("Attachment"); pAtt2.Parent = pRing
	local pEm2 = Instance.new("ParticleEmitter"); pEm2.Parent = pAtt2
	pEm2.Rate = 8
	pEm2.Speed = NumberRange.new(2, 4)
	pEm2.Lifetime = NumberRange.new(2, 4)
	pEm2.SpreadAngle = Vector2.new(180, 180)
	pEm2.Acceleration = Vector3.new(0, 0.5, 0)
	pEm2.Texture = "rbxasset://textures/particles/sparkle_02.png"
	pEm2.Color = ColorSequence.new(C.portalGlow)
	pEm2.Size = NumberSequence.new(0.5)
	pEm2.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.6),
		NumberSequenceKeypoint.new(0.5, 0.3),
		NumberSequenceKeypoint.new(1, 1),
	})
	pEm2.LightEmission = 1
	pEm2.LightInfluence = 0

	-- Dust motes
	local dSrc = pt("DSrc", Vector3.new(1, 1, 1), Vector3.new(CX, FY + 18, CZ), C.fluorescentDim, Enum.Material.SmoothPlastic, Workspace)
	dSrc.Transparency = 1
	local dAtt = Instance.new("Attachment"); dAtt.Parent = dSrc
	local dEm = Instance.new("ParticleEmitter"); dEm.Parent = dAtt
	dEm.Rate = 5
	dEm.Speed = NumberRange.new(0.3, 1)
	dEm.Lifetime = NumberRange.new(8, 16)
	dEm.SpreadAngle = Vector2.new(70, 70)
	dEm.Acceleration = Vector3.new(0, 0.1, 0)
	dEm.Texture = "rbxasset://textures/particles/sparkle_02.png"
	dEm.Color = ColorSequence.new(Color3.fromRGB(180, 170, 200))
	dEm.Size = NumberSequence.new(0.2)
	dEm.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 0.85),
		NumberSequenceKeypoint.new(0.5, 0.65),
		NumberSequenceKeypoint.new(1, 1),
	})
	dEm.LightEmission = 0.2
	dEm.LightInfluence = 0.3
end

-- ============================================================
-- WALLS + ARCHES
-- ============================================================

local function buildWalls()
	-- Back wall
	pt("WallBack", Vector3.new(W, H, T), Vector3.new(CX, WY, CZ - HD + T / 2), C.stone, Enum.Material.Slate, Workspace)

	-- Decorative arches on back wall
	for i = 0, 3 do
		local ax = CX - 35 + i * 23
		local aw = 8
		local ah = 26
		pt("ABack_" .. i, Vector3.new(aw - 0.8, ah, 0.1), Vector3.new(ax, FY + ah / 2 + 3, CZ - HD + T + 0.05), C.obsidian, Enum.Material.Slate, Workspace)
		pt("AFL_" .. i, Vector3.new(0.5, ah + 2, 0.15), Vector3.new(ax - aw / 2, FY + ah / 2 + 3, CZ - HD + T + 0.08), C.stoneLight, Enum.Material.Slate, Workspace)
		pt("AFR_" .. i, Vector3.new(0.5, ah + 2, 0.15), Vector3.new(ax + aw / 2, FY + ah / 2 + 3, CZ - HD + T + 0.08), C.stoneLight, Enum.Material.Slate, Workspace)
		pt("AFT_" .. i, Vector3.new(aw + 1, 0.5, 0.15), Vector3.new(ax, FY + ah + 4, CZ - HD + T + 0.08), C.stoneLight, Enum.Material.Slate, Workspace)
	end

	-- Front wall (with arch opening)
	pt("WallFrontL", Vector3.new(42, H, T), Vector3.new(CX - 37, WY, CZ + HD - T / 2), C.stone, Enum.Material.Slate, Workspace)
	pt("WallFrontR", Vector3.new(42, H, T), Vector3.new(CX + 37, WY, CZ + HD - T / 2), C.stone, Enum.Material.Slate, Workspace)
	-- Fill gaps between walls and arch pillars
	pt("WallFillL", Vector3.new(6.3, H, T), Vector3.new(CX - 12.85, WY, CZ + HD - T / 2), C.stone, Enum.Material.Slate, Workspace)
	pt("WallFillR", Vector3.new(6.3, H, T), Vector3.new(CX + 12.85, WY, CZ + HD - T / 2), C.stone, Enum.Material.Slate, Workspace)

	-- Entrance arch
	local eW = 18
	local eH = 24
	pt("EntL", Vector3.new(1.4, eH, T + 0.2), Vector3.new(CX - eW / 2, FY + eH / 2, CZ + HD - T / 2), C.stoneLight, Enum.Material.Slate, Workspace)
	pt("EntR", Vector3.new(1.4, eH, T + 0.2), Vector3.new(CX + eW / 2, FY + eH / 2, CZ + HD - T / 2), C.stoneLight, Enum.Material.Slate, Workspace)
	pt("EntTop", Vector3.new(eW + 2.8, 1.4, T + 0.2), Vector3.new(CX, FY + eH, CZ + HD - T / 2), C.stoneLight, Enum.Material.Slate, Workspace)

	-- Warning lights above entrance
	for i = 0, 6 do
		local wx = CX - 8 + i * 3
		local wl = pt("WL_" .. i, Vector3.new(0.5, 0.5, 0.3), Vector3.new(wx, FY + eH + 3, CZ + HD - T / 2 - 0.1), C.gold, Enum.Material.Neon, Workspace)
		local wll = Instance.new("PointLight")
		wll.Color = C.gold
		wll.Brightness = 0.8
		wll.Range = 5
		wll.Parent = wl
	end

	-- Left wall
	pt("WallLeft", Vector3.new(T, H, D), Vector3.new(CX - HW + T / 2, WY, CZ), C.stone, Enum.Material.Slate, Workspace)
	for i = 0, 4 do
		local az = CZ - 30 + i * 15
		local aw = 9
		local ah = 20
		pt("LArc_" .. i, Vector3.new(0.1, ah, aw - 1), Vector3.new(CX - HW + T + 0.05, FY + ah / 2 + 2, az), C.obsidian, Enum.Material.Slate, Workspace)
		pt("LFL_" .. i, Vector3.new(0.15, ah + 2, 0.5), Vector3.new(CX - HW + T + 0.08, FY + ah / 2 + 2, az - aw / 2), C.stoneLight, Enum.Material.Slate, Workspace)
		pt("LFR_" .. i, Vector3.new(0.15, ah + 2, 0.5), Vector3.new(CX - HW + T + 0.08, FY + ah / 2 + 2, az + aw / 2), C.stoneLight, Enum.Material.Slate, Workspace)
		pt("LFT_" .. i, Vector3.new(0.15, 0.5, aw + 1), Vector3.new(CX - HW + T + 0.08, FY + ah + 3, az), C.stoneLight, Enum.Material.Slate, Workspace)
	end

	-- Right wall
	pt("WallRight", Vector3.new(T, H, D), Vector3.new(CX + HW - T / 2, WY, CZ), C.stone, Enum.Material.Slate, Workspace)
	for i = 0, 4 do
		local az = CZ - 30 + i * 15
		local aw = 9
		local ah = 20
		pt("RArc_" .. i, Vector3.new(0.1, ah, aw - 1), Vector3.new(CX + HW - T - 0.05, FY + ah / 2 + 2, az), C.obsidian, Enum.Material.Slate, Workspace)
		pt("RFL_" .. i, Vector3.new(0.15, ah + 2, 0.5), Vector3.new(CX + HW - T - 0.08, FY + ah / 2 + 2, az - aw / 2), C.stoneLight, Enum.Material.Slate, Workspace)
		pt("RFR_" .. i, Vector3.new(0.15, ah + 2, 0.5), Vector3.new(CX + HW - T - 0.08, FY + ah / 2 + 2, az + aw / 2), C.stoneLight, Enum.Material.Slate, Workspace)
		pt("RFT_" .. i, Vector3.new(0.15, 0.5, aw + 1), Vector3.new(CX + HW - T - 0.08, FY + ah + 3, az), C.stoneLight, Enum.Material.Slate, Workspace)
	end

	-- Blood stains
	pt("BS1", Vector3.new(4, 0.03, 2), Vector3.new(CX + 15, FY + 0.08, CZ - 10), C.blood, Enum.Material.SmoothPlastic, Workspace)
	pt("BS2", Vector3.new(2, 0.03, 5), Vector3.new(CX - 20, FY + 0.08, CZ + 6), C.bloodDark, Enum.Material.SmoothPlastic, Workspace)
	pt("BTrail", Vector3.new(0.25, 0.03, 12), Vector3.new(CX + 15, FY + 0.08, CZ - 4), C.blood, Enum.Material.SmoothPlastic, Workspace)

	-- Hanging chains on walls
	for i = 0, 7 do
		local cx2 = CX - 42 + i * 12
		local cz2 = CZ - 28 + (i % 3) * 25
		local cl = 4 + (i % 4) * 4
		pt("Chain_" .. i, Vector3.new(0.08, cl, 0.08), Vector3.new(cx2, FY + 2 + cl / 2, cz2), C.ironDark, Enum.Material.Metal, Workspace)
	end
end

-- ============================================================
-- VAULTED CEILING + LIGHTS
-- ============================================================

local function buildCeiling(): { PointLight }
	pt("CeilBase", Vector3.new(W, 0.5, D), Vector3.new(CX, CY + 0.25, CZ), C.obsidian, Enum.Material.Concrete, Workspace)
	local lights: { PointLight } = {}

	-- Vaulted ribs
	for i = 0, 10 do
		local rz = CZ - 34 + i * 7
		local rh = 8
		pt("Rib_" .. i, Vector3.new(W - 4, rh, 0.6), Vector3.new(CX, CY - rh / 2 + 1, rz), C.stoneDark, Enum.Material.Slate, Workspace)
		pt("RCap_" .. i, Vector3.new(W - 4, 0.3, 0.8), Vector3.new(CX, CY - rh + 1.2, rz), C.stoneLight, Enum.Material.Slate, Workspace)
	end
	for i = 0, 6 do
		local rx = CX - 46 + i * 15
		local rh = 8
		pt("CRib_" .. i, Vector3.new(0.6, rh, D - 8), Vector3.new(rx, CY - rh / 2 + 1, CZ), C.stoneDark, Enum.Material.Slate, Workspace)
	end

	-- Chandelier ring
	cyl("Chandelier", 16, 0.5, Vector3.new(CX, CY - 10, CZ), C.ironDark, Enum.Material.Metal, Workspace)
	cyl("ChandelierIn", 11, 0.3, Vector3.new(CX, CY - 9.5, CZ), C.iron, Enum.Material.Metal, Workspace)
	local chGlow = pt("ChGlow", Vector3.new(0.4, 0.12, 0.4), Vector3.new(CX, CY - 10, CZ), C.neonRed, Enum.Material.Neon, Workspace)
	local chLight = Instance.new("PointLight")
	chLight.Color = C.bloodBright
	chLight.Brightness = 4
	chLight.Range = 35
	chLight.Shadows = true
	chLight.Parent = chGlow
	table.insert(lights, chLight)

	-- Chandelier chains
	for _, angle in { 0, 45, 90, 135, 180, 225, 270, 315 } do
		local rad = math.rad(angle)
		local cx2 = CX + math.cos(rad) * 7.5
		local cz2 = CZ + math.sin(rad) * 7.5
		local cl = 2 + math.random() * 5
		pt("ChCh_" .. angle, Vector3.new(0.06, cl, 0.06), Vector3.new(cx2, CY - 10 - cl / 2, cz2), C.ironDark, Enum.Material.Metal, Workspace)
	end

	-- Spotlights
	for _, sp in {
		{ CX - 35, CZ - 18, C.bloodBright, 5, 70 },
		{ CX + 35, CZ - 18, C.bloodBright, 5, 70 },
		{ CX - 35, CZ + 18, C.neonBlue, 5, 70 },
		{ CX + 35, CZ + 18, C.neonBlue, 5, 70 },
		{ CX, CZ, C.portalGlow, 6, 80 },
	} do
		local sx, sz, sCol, sBr, sR = sp[1], sp[2], sp[3], sp[4], sp[5]
		local sb = pt("Spot_" .. sx .. "_" .. sz, Vector3.new(1, 0.6, 1), Vector3.new(sx, CY - 0.6, sz), C.ironDark, Enum.Material.Metal, Workspace)
		local sl = Instance.new("SpotLight")
		sl.Color = sCol
		sl.Brightness = sBr
		sl.Range = sR
		sl.Angle = 120
		sl.Face = Enum.NormalId.Bottom
		sl.Shadows = true
		sl.Parent = sb
	end

	-- Fill lights
	for _, pos in {
		Vector3.new(CX - 40, FY + 10, CZ - 25),
		Vector3.new(CX + 40, FY + 10, CZ - 25),
		Vector3.new(CX - 40, FY + 10, CZ + 25),
		Vector3.new(CX + 40, FY + 10, CZ + 25),
		Vector3.new(CX - 20, FY + 5, CZ),
		Vector3.new(CX + 20, FY + 5, CZ),
		Vector3.new(CX, FY + 5, CZ - 20),
		Vector3.new(CX, FY + 5, CZ + 20),
	} do
		local fb = pt("Fill_" .. pos.X .. "_" .. pos.Z, Vector3.new(0.25, 0.25, 0.25), pos, Color3.fromRGB(180, 170, 200), Enum.Material.Neon, Workspace)
		local fl = Instance.new("PointLight")
		fl.Color = Color3.fromRGB(180, 170, 200)
		fl.Brightness = 1.2
		fl.Range = 25
		fl.Shadows = false
		fl.Parent = fb
	end

	return lights
end

-- ============================================================
-- PILLARS
-- ============================================================

local function buildPillars()
	local positions = {
		{ CX - PIT - 5, CZ - PIT - 5 },
		{ CX - PIT - 5, CZ + PIT + 5 },
		{ CX + PIT + 5, CZ - PIT - 5 },
		{ CX + PIT + 5, CZ + PIT + 5 },
	}
	for i, pp in positions do
		local px, pz = pp[1], pp[2]
		pt("Pil_" .. i, Vector3.new(5, H - 4, 5), Vector3.new(px, FY + (H - 4) / 2, pz), C.stoneDark, Enum.Material.Slate, Workspace)
		pt("PilB_" .. i, Vector3.new(6, 1.2, 6), Vector3.new(px, FY + 0.6, pz), C.stoneLight, Enum.Material.Slate, Workspace)
		pt("PilC_" .. i, Vector3.new(6, 2, 6), Vector3.new(px, FY + H - 3, pz), C.stoneLight, Enum.Material.Slate, Workspace)
		-- Grooves
		for g = 0, 3 do
			local gy = FY + 5 + g * 9
			pt("PG_" .. i .. "_" .. g, Vector3.new(5.2, 0.15, 0.35), Vector3.new(px, gy, pz - 2.5), C.obsidian, Enum.Material.Slate, Workspace)
			pt("PG2_" .. i .. "_" .. g, Vector3.new(0.35, 0.15, 5.2), Vector3.new(px - 2.5, gy, pz), C.obsidian, Enum.Material.Slate, Workspace)
		end
		-- Rune
		local rune = pt("PRune_" .. i, Vector3.new(0.6, 0.8, 0.08), Vector3.new(px, FY + 14, pz - 2.52), C.neonRed, Enum.Material.Neon, Workspace)
		local rl = Instance.new("PointLight")
		rl.Color = C.bloodBright
		rl.Brightness = 0.8
		rl.Range = 6
		rl.Parent = rune
	end
end

-- ============================================================
-- BRIDGES — crossing the void
-- ============================================================

local function buildBridges()
	local bY = FY + 0.8
	-- North
	pt("BrN", Vector3.new(PIT * 2 - 2, 0.6, 4.5), Vector3.new(CX, bY, CZ + PIT + 2.25), C.stoneDark, Enum.Material.Slate, Workspace)
	pt("BrNR_L", Vector3.new(PIT * 2 - 2, 0.1, 0.15), Vector3.new(CX, bY + 1.4, CZ + PIT + 0.2), C.ironDark, Enum.Material.Metal, Workspace)
	pt("BrNR_R", Vector3.new(PIT * 2 - 2, 0.1, 0.15), Vector3.new(CX, bY + 1.4, CZ + PIT + 4.3), C.ironDark, Enum.Material.Metal, Workspace)
	-- South
	pt("BrS", Vector3.new(PIT * 2 - 2, 0.6, 4.5), Vector3.new(CX, bY, CZ - PIT - 2.25), C.stoneDark, Enum.Material.Slate, Workspace)
	pt("BrSR_L", Vector3.new(PIT * 2 - 2, 0.1, 0.15), Vector3.new(CX, bY + 1.4, CZ - PIT - 0.2), C.ironDark, Enum.Material.Metal, Workspace)
	pt("BrSR_R", Vector3.new(PIT * 2 - 2, 0.1, 0.15), Vector3.new(CX, bY + 1.4, CZ - PIT - 4.3), C.ironDark, Enum.Material.Metal, Workspace)
	-- West
	pt("BrW", Vector3.new(4.5, 0.6, PIT * 2 - 2), Vector3.new(CX - PIT - 2.25, bY, CZ), C.stoneDark, Enum.Material.Slate, Workspace)
	pt("BrWR_L", Vector3.new(0.15, 0.1, PIT * 2 - 2), Vector3.new(CX - PIT - 0.2, bY + 1.4, CZ), C.ironDark, Enum.Material.Metal, Workspace)
	pt("BrWR_R", Vector3.new(0.15, 0.1, PIT * 2 - 2), Vector3.new(CX - PIT - 4.3, bY + 1.4, CZ), C.ironDark, Enum.Material.Metal, Workspace)
	-- East
	pt("BrE", Vector3.new(4.5, 0.6, PIT * 2 - 2), Vector3.new(CX + PIT + 2.25, bY, CZ), C.stoneDark, Enum.Material.Slate, Workspace)
	pt("BrER_L", Vector3.new(0.15, 0.1, PIT * 2 - 2), Vector3.new(CX + PIT + 0.2, bY + 1.4, CZ), C.ironDark, Enum.Material.Metal, Workspace)
	pt("BrER_R", Vector3.new(0.15, 0.1, PIT * 2 - 2), Vector3.new(CX + PIT + 4.3, bY + 1.4, CZ), C.ironDark, Enum.Material.Metal, Workspace)
end

-- ============================================================
-- BUNKER TITLE — colossal glowing letters
-- ============================================================

local function buildTitle()
	local title = Instance.new("Model")
	title.Name = "BUNKER_3D_Title"
	title.Parent = lobbyModel

	local glyphs = {
		B = { "top", "middle", "bottom", "leftTop", "leftBottom", "rightTop", "rightBottom" },
		U = { "bottom", "leftTop", "leftBottom", "rightTop", "rightBottom" },
		N = { "leftTop", "leftBottom", "rightTop", "rightBottom", "diagDown" },
		K = { "leftTop", "leftBottom", "diagUp", "diagDown" },
		E = { "top", "middle", "bottom", "leftTop", "leftBottom" },
		R = { "top", "middle", "leftTop", "leftBottom", "rightTop", "diagDown" },
	}
	local seg = {
		top = { Vector3.new(3, 0.45, 0.55), Vector3.new(0, 2.05, 0), 0 },
		middle = { Vector3.new(2.8, 0.4, 0.55), Vector3.new(0, 0, 0), 0 },
		bottom = { Vector3.new(3, 0.45, 0.55), Vector3.new(0, -2.05, 0), 0 },
		leftTop = { Vector3.new(0.45, 2.2, 0.55), Vector3.new(-1.35, 1.02, 0), 0 },
		leftBottom = { Vector3.new(0.45, 2.2, 0.55), Vector3.new(-1.35, -1.02, 0), 0 },
		rightTop = { Vector3.new(0.45, 2.2, 0.55), Vector3.new(1.35, 1.02, 0), 0 },
		rightBottom = { Vector3.new(0.45, 2.2, 0.55), Vector3.new(1.35, -1.02, 0), 0 },
		diagUp = { Vector3.new(0.45, 2.7, 0.55), Vector3.new(0.6, 0.95, 0), -37 },
		diagDown = { Vector3.new(0.45, 4.5, 0.55), Vector3.new(0, 0, 0), 34 },
	}
	local letters = { "B", "U", "N", "K", "E", "R" }
	local startX = CX - 14.5
	local titleY = FY + 20
	local titleZ = CZ - HD + T + 1

	for idx, letter in letters do
		local lx = startX + (idx - 1) * 5.6
		for si, sn in glyphs[letter] do
			local d = seg[sn]
			local sz = d[1] :: Vector3
			local off = d[2] :: Vector3
			local ang = d[3] :: number
			-- Glow layer
			local gb = pt(string.format("G_%s_%d", letter, si), sz + Vector3.new(0.25, 0.25, -0.3), Vector3.new(lx, titleY, titleZ - 0.4) + off, C.neonRed, Enum.Material.Neon, title)
			gb.CFrame *= CFrame.Angles(0, 0, math.rad(ang))
			gb.Transparency = 0.2
			-- Metal layer
			local mb = pt(string.format("M_%s_%d", letter, si), sz, Vector3.new(lx, titleY, titleZ) + off, C.rustDark, Enum.Material.CorrodedMetal, title)
			mb.CFrame *= CFrame.Angles(0, 0, math.rad(ang))
		end
	end

	-- Title glow
	local la = pt("TitleBL", Vector3.new(0.3, 0.3, 0.3), Vector3.new(CX, titleY, titleZ - 0.9), C.neonRed, Enum.Material.Neon, title)
	la.Transparency = 1
	local bl = Instance.new("PointLight")
	bl.Color = C.bloodBright
	bl.Brightness = 1
	bl.Range = 15
	bl.Shadows = false
	bl.Parent = la

	-- Blood drips
	for i = 0, 5 do
		pt("BD_" .. i, Vector3.new(0.15, 1.5 + math.random() * 3, 0.08), Vector3.new(startX + i * 5 + math.random() * 2, FY + 8 - math.random() * 4, titleZ - 0.2), C.bloodBright, Enum.Material.SmoothPlastic, title)
	end
end

-- ============================================================
-- TELEPORTER PLATFORMS
-- ============================================================

local teleportSigns: { TextLabel } = {}

local function buildTeleportPads()
	local padY = FY + 2.0
	local padPositions = {
		{ CX - 38, CZ + 24, "1", "ZONE 1", C.neonBlue },
		{ CX - 38, CZ - 24, "2", "START GAME", C.neonRed },
		{ CX + 38, CZ + 24, "3", "ZONE 1", C.neonBlue },
		{ CX + 38, CZ - 24, "4", "START GAME", C.neonRed },
	}

	for _, pp in padPositions do
		local px, pz, id, label, coreColor = pp[1], pp[2], pp[3], pp[4], pp[5]

		-- Base
		pt("TP" .. id .. "Base", Vector3.new(10, 1.4, 10), Vector3.new(px, padY, pz), C.stoneDark, Enum.Material.Slate, Workspace)
		-- Step 1
		pt("TP" .. id .. "S1", Vector3.new(8, 0.6, 8), Vector3.new(px, padY + 1.6, pz), C.stoneLight, Enum.Material.Slate, Workspace)
		-- Step 2
		pt("TP" .. id .. "S2", Vector3.new(6.5, 0.5, 6.5), Vector3.new(px, padY + 2.5, pz), C.obsidian, Enum.Material.Slate, Workspace)
		-- Top
		pt("TP" .. id .. "Top", Vector3.new(5.6, 0.35, 5.6), Vector3.new(px, padY + 3.2, pz), C.stoneDark, Enum.Material.Slate, Workspace)
		-- Glow ring
		cyl("TP" .. id .. "Ring", 5.2, 0.12, Vector3.new(px, padY + 3.4, pz), coreColor, Enum.Material.Neon, Workspace)

		-- Stairs
		local stairDir = if px < 0 then 1 else -1
		for si = 0, 3 do
			local sy = FY + 0.35 + si * 0.55
			local sx = px + stairDir * (5 + si * 1.2 + 0.5)
			pt("TP" .. id .. "St_" .. si, Vector3.new(6, 0.55, 1.3), Vector3.new(sx, sy, pz), C.stoneLight, Enum.Material.Slate, Workspace)
		end

		-- Corner crystals
		for _, angle in { 45, 135, 225, 315 } do
			local rad = math.rad(angle)
			local cx2 = px + math.cos(rad) * 4.2
			local cz2 = pz + math.sin(rad) * 4.2
			pt("TP" .. id .. "Pil_" .. angle, Vector3.new(0.7, 3, 0.7), Vector3.new(cx2, padY + 1.6, cz2), C.stoneLight, Enum.Material.Slate, Workspace)
			local cry = pt("TP" .. id .. "Cry_" .. angle, Vector3.new(0.35, 1, 0.35), Vector3.new(cx2, padY + 3.6, cz2), coreColor, Enum.Material.Neon, Workspace)
			local cl = Instance.new("PointLight")
			cl.Color = coreColor
			cl.Brightness = 1
			cl.Range = 7
			cl.Parent = cry
		end

		-- Beacon
		local beacon = pt("TP" .. id .. "Beacon", Vector3.new(6, 1.8, 6), Vector3.new(px, padY + 4.2, pz), coreColor, Enum.Material.SmoothPlastic, Workspace)
		beacon.Transparency = 0.92
		beacon.CanCollide = false
		beacon.CanQuery = true
		beacon.CanTouch = true
		beacon:SetAttribute("TeleportPad", "BunkerGame")
		beacon:SetAttribute("DisplayName", label)
		beacon:SetAttribute("TargetPlaceId", 72688245649120)

		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Launch"
		prompt.ObjectText = label .. " -> BunkerGame"
		prompt.KeyboardKeyCode = Enum.KeyCode.E
		prompt.GamepadKeyCode = Enum.KeyCode.ButtonX
		prompt.HoldDuration = 0.35
		prompt.MaxActivationDistance = 9
		prompt.RequiresLineOfSight = false
		prompt.Parent = beacon

		local pl = Instance.new("PointLight")
		pl.Color = coreColor
		pl.Brightness = 1.2
		pl.Range = 14
		pl.Shadows = false
		pl.Parent = beacon

		-- Particle fountain
		local bp = pt("TP" .. id .. "Beam", Vector3.new(0.3, 0.3, 0.3), Vector3.new(px, padY + 3.5, pz), coreColor, Enum.Material.Neon, Workspace)
		bp.Transparency = 1
		local ba = Instance.new("Attachment"); ba.Parent = bp
		local be = Instance.new("ParticleEmitter"); be.Parent = ba
		be.Rate = 20
		be.Speed = NumberRange.new(3, 7)
		be.Lifetime = NumberRange.new(1, 2)
		be.SpreadAngle = Vector2.new(10, 10)
		be.Acceleration = Vector3.new(0, 8, 0)
		be.Texture = "rbxasset://textures/particles/sparkle_02.png"
		be.Color = ColorSequence.new({
			ColorSequenceKeypoint.new(0, coreColor),
			ColorSequenceKeypoint.new(1, Color3.new(1, 1, 1)),
		})
		be.Size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.6),
			NumberSequenceKeypoint.new(0.5, 0.4),
			NumberSequenceKeypoint.new(1, 0.05),
		})
		be.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.6),
			NumberSequenceKeypoint.new(0.3, 0.2),
			NumberSequenceKeypoint.new(1, 1),
		})
		be.LightEmission = 0.8
		be.LightInfluence = 0

		-- Sign
		local sp = pt("TP" .. id .. "Sign", Vector3.new(6.5, 1.2, 0.15), Vector3.new(px, padY + 8, pz - 3.5), C.obsidian, Enum.Material.Slate, Workspace)
		local sg = Instance.new("SurfaceGui")
		sg.Face = Enum.NormalId.Back
		sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		sg.PixelsPerStud = 110
		sg.LightInfluence = 0.1
		sg.Parent = sp
		local sbg = Instance.new("Frame")
		sbg.Size = UDim2.fromScale(1, 1)
		sbg.BackgroundColor3 = Color3.fromRGB(4, 10, 6)
		sbg.BorderSizePixel = 0
		sbg.Parent = sg
		local sl = Instance.new("TextLabel")
		sl.Name = "SignText"
		sl.Size = UDim2.fromScale(0.92, 0.7)
		sl.Position = UDim2.fromScale(0.04, 0.15)
		sl.BackgroundTransparency = 1
		sl.Text = label
		sl.TextColor3 = C.screenGlow
		sl.TextScaled = true
		sl.Font = Enum.Font.Code
		sl.TextStrokeColor3 = Color3.fromRGB(4, 24, 8)
		sl.TextStrokeTransparency = 0.25
		sl.Parent = sbg
		-- Cracks
		for ci, c in { { 0.18, 0.32, 28 }, { 0.72, 0.22, -38 }, { 0.84, 0.72, 42 } } do
			local cl2 = Instance.new("Frame")
			cl2.Name = "Ck" .. ci
			cl2.AnchorPoint = Vector2.new(0.5, 0.5)
			cl2.Position = UDim2.fromScale(c[1], c[2])
			cl2.Size = UDim2.fromOffset(2, 54)
			cl2.Rotation = c[3]
			cl2.BackgroundColor3 = Color3.fromRGB(18, 30, 22)
			cl2.BorderSizePixel = 0
			cl2.ZIndex = 3
			cl2.Parent = sbg
		end
		table.insert(teleportSigns, sl)
	end
end

-- ============================================================
-- RECEPTION DESK
-- ============================================================

local function buildDesk()
	local dx, dz = CX, CZ - 22
	pt("DTop", Vector3.new(20, 0.55, 5.5), Vector3.new(dx, FY + 4.2, dz), C.iron, Enum.Material.CorrodedMetal, Workspace)
	pt("DFront", Vector3.new(20, 3.8, 0.6), Vector3.new(dx, FY + 2.1, dz + 3.05), C.stoneDark, Enum.Material.Slate, Workspace)
	pt("DBack", Vector3.new(20, 3.8, 0.45), Vector3.new(dx, FY + 2.1, dz - 3.05), C.ironDark, Enum.Material.CorrodedMetal, Workspace)
	pt("DSL", Vector3.new(0.6, 3.8, 6.1), Vector3.new(dx - 9.7, FY + 2.1, dz), C.stoneDark, Enum.Material.Slate, Workspace)
	pt("DSR", Vector3.new(0.6, 3.8, 6.1), Vector3.new(dx + 9.7, FY + 2.1, dz), C.stoneDark, Enum.Material.Slate, Workspace)

	for i = 0, 2 do
		local mx = dx - 6 + i * 6
		pt("MB_" .. i, Vector3.new(1.6, 0.15, 1.4), Vector3.new(mx, FY + 4.4, dz), C.ironDark, Enum.Material.Metal, Workspace)
		pt("MS_" .. i, Vector3.new(0.25, 0.7, 0.25), Vector3.new(mx, FY + 4.8, dz), C.ironDark, Enum.Material.Metal, Workspace)
		pt("MM_" .. i, Vector3.new(3, 2.2, 0.3), Vector3.new(mx, FY + 6.4, dz), C.ironDark, Enum.Material.Metal, Workspace)
		local scr = pt("MSc_" .. i, Vector3.new(2.6, 1.8, 0.05), Vector3.new(mx, FY + 6.4, dz + 0.18), C.screen, Enum.Material.SmoothPlastic, Workspace)
		scr.CanCollide = false
		local sg2 = Instance.new("SurfaceGui")
		sg2.Name = "SG"
		sg2.Face = Enum.NormalId.Back
		sg2.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		sg2.PixelsPerStud = 130
		sg2.LightInfluence = 0.1
		sg2.Parent = scr
		for j = 1, 6 do
			local tl = Instance.new("TextLabel")
			tl.Name = "CL" .. j
			tl.Size = UDim2.new(0.94, 0, 0.13, 0)
			tl.Position = UDim2.new(0.03, 0, 0.04 + (j - 1) * 0.155, 0)
			tl.BackgroundTransparency = 1
			tl.TextColor3 = C.screenGlow
			tl.TextScaled = true
			tl.Font = Enum.Font.Code
			tl.TextXAlignment = Enum.TextXAlignment.Left
			tl.Text = string.format("SYS/%02d  %04X  %s", j, math.random(0, 65535), if j % 2 == 0 then "ON" else "LOCK")
			tl.Parent = sg2
		end
		task.spawn(function()
			local lines = {}
			for j = 1, 6 do
				local ch = sg2:FindFirstChild("CL" .. j)
				if ch then table.insert(lines, ch :: TextLabel) end
			end
			while true do
				for _, l2 in lines do
					l2.Text = string.format("%04X:%04X  %s", math.random(0, 65535), math.random(0, 65535), if math.random() > 0.25 then "OK" else "WARN")
				end
				task.wait(0.4 + math.random() * 0.3)
			end
		end)
	end

	local lamp = pt("Lamp", Vector3.new(0.45, 0.7, 0.45), Vector3.new(dx + 7, FY + 4.5, dz - 1.8), C.ironDark, Enum.Material.Metal, Workspace)
	local lg = pt("LampG", Vector3.new(0.35, 0.12, 0.35), Vector3.new(dx + 7, FY + 5.1, dz - 1.8), Color3.fromRGB(255, 200, 100), Enum.Material.Neon, Workspace)
	local ll = Instance.new("PointLight")
	ll.Color = Color3.fromRGB(255, 200, 100)
	ll.Brightness = 2
	ll.Range = 14
	ll.Parent = lg

	pt("KB", Vector3.new(2.8, 0.1, 1.1), Vector3.new(dx - 2, FY + 4.42, dz + 2.2), C.ironDark, Enum.Material.SmoothPlastic, Workspace)
	pt("Mouse", Vector3.new(0.45, 0.08, 0.8), Vector3.new(dx + 1.5, FY + 4.42, dz + 2.4), C.ironDark, Enum.Material.SmoothPlastic, Workspace)
	pt("Papers", Vector3.new(1.8, 0.18, 2.2), Vector3.new(dx + 6, FY + 4.42, dz + 1.2), C.fluorescent, Enum.Material.SmoothPlastic, Workspace)
	pt("Mug", Vector3.new(0.4, 0.45, 0.4), Vector3.new(dx + 8, FY + 4.62, dz + 0.6), C.bloodDark, Enum.Material.SmoothPlastic, Workspace)
end

-- ============================================================
-- ENTRANCE DOORS
-- ============================================================

local function buildDoor()
	local dz = CZ + HD - T / 2
	pt("DoorL", Vector3.new(8.5, 22, 0.7), Vector3.new(CX - 5.5, FY + 11, dz), C.ironDark, Enum.Material.CorrodedMetal, Workspace)
	pt("DoorR", Vector3.new(8.5, 22, 0.7), Vector3.new(CX + 5.5, FY + 11, dz), C.ironDark, Enum.Material.CorrodedMetal, Workspace)
	for _, dx2 in { -10, -7, -4, -1, 2, 5, 8, 11 } do
		for _, dy2 in { 3, 6, 9, 12, 15, 18 } do
			pt("Bolt_" .. dx2 .. "_" .. dy2, Vector3.new(0.25, 0.25, 0.12), Vector3.new(CX + dx2, FY + dy2, dz + 0.45), C.steel, Enum.Material.Metal, Workspace)
		end
	end
	pt("HndL", Vector3.new(0.25, 1.8, 0.7), Vector3.new(CX - 2, FY + 11, dz + 0.55), C.steel, Enum.Material.Metal, Workspace)
	pt("HndR", Vector3.new(0.25, 1.8, 0.7), Vector3.new(CX + 2, FY + 11, dz + 0.55), C.steel, Enum.Material.Metal, Workspace)
	pt("Warn", Vector3.new(12, 2.5, 0.15), Vector3.new(CX, FY + 26, dz + 0.07), C.bloodBright, Enum.Material.SmoothPlastic, Workspace)
	pt("WarnT", Vector3.new(10, 0.8, 0.04), Vector3.new(CX, FY + 26.4, dz + 0.16), C.fluorescent, Enum.Material.Neon, Workspace)
end

-- ============================================================
-- PROPS
-- ============================================================

local function buildProps()
	-- Pipes along ceiling edges
	for i = 0, 8 do
		local pz = CZ - 34 + i * 8
		pt("PipeL_" .. i, Vector3.new(0.45, 0.45, 7), Vector3.new(CX - HW + 4, CY - 2.5, pz), C.copper, Enum.Material.CorrodedMetal, Workspace)
		pt("PipeR_" .. i, Vector3.new(0.45, 0.45, 7), Vector3.new(CX + HW - 4, CY - 2.5, pz), C.copper, Enum.Material.CorrodedMetal, Workspace)
	end

	-- Hanging cables
	for i = 1, 12 do
		local cx2 = CX - 42 + i * 7
		local cz2 = CZ - 25 + math.random(0, 500) / 10
		local hl = 3 + math.random() * 10
		pt("Cab_" .. i, Vector3.new(0.06, hl, 0.06), Vector3.new(cx2, CY - 1.5 - hl / 2, cz2),
			if math.random() > 0.5 then C.ironDark else C.copper, Enum.Material.Metal, Workspace)
	end

	-- Barrels
	for i, bp in {
		{ CX - 48, CZ - 32 }, { CX - 46, CZ - 35 }, { CX - 50, CZ - 30 },
		{ CX + 48, CZ + 30 }, { CX + 46, CZ + 33 },
		{ CX - 46, CZ + 34 }, { CX - 48, CZ + 37 },
		{ CX + 44, CZ - 34 },
	} do
		local bx, bz = bp[1], bp[2]
		pt("Brl_" .. i, Vector3.new(2.2, 3.5, 2.2), Vector3.new(bx, FY + 1.75, bz),
			if i % 2 == 0 then C.ironDark else C.rust, Enum.Material.Metal, Workspace)
		pt("BrlR_" .. i, Vector3.new(2.3, 0.25, 2.3), Vector3.new(bx, FY + 3.5, bz), C.steel, Enum.Material.Metal, Workspace)
	end

	-- Crates
	for i, cp in {
		{ CX + 46, CZ - 28 }, { CX + 48, CZ - 24 }, { CX + 47, CZ - 32 },
		{ CX - 44, CZ + 28 }, { CX - 46, CZ + 31 },
		{ CX + 42, CZ + 28 },
	} do
		local cx2, cz2 = cp[1], cp[2]
		local s = 2.8 + math.random(0, 10) / 10
		pt("Crt_" .. i, Vector3.new(s, s, s), Vector3.new(cx2, FY + s / 2, cz2), C.rust, Enum.Material.WoodPlanks, Workspace)
		pt("CrtB_" .. i, Vector3.new(s + 0.12, 0.12, s + 0.12), Vector3.new(cx2, FY + s / 3, cz2), C.ironDark, Enum.Material.Metal, Workspace)
	end

	-- Electrical box
	local eb = pt("Elec", Vector3.new(3, 3.5, 0.9), Vector3.new(CX + HW - T - 0.45, FY + 5.5, CZ - 7), C.ironDark, Enum.Material.Metal, Workspace)
	pt("SW", Vector3.new(0.06, 2.5, 0.06), Vector3.new(CX + HW - T - 0.12, FY + 4, CZ - 7), C.copper, Enum.Material.Neon, Workspace)
	local sg2 = pt("SG2", Vector3.new(0.25, 0.25, 0.25), Vector3.new(CX + HW - T - 0.12, FY + 2.8, CZ - 7), C.ember, Enum.Material.Neon, Workspace)
	local sl2 = Instance.new("PointLight")
	sl2.Color = C.ember
	sl2.Brightness = 0.7
	sl2.Range = 5
	sl2.Parent = sg2
end

-- ============================================================
-- ROTATING RING ANIMATION
-- ============================================================

local ringPart: Part?
local ringPart2: Part?

local function buildRotatingRings()
	-- Create rings that will be rotated via Heartbeat
	local r1 = cyl("RotRing1", 20, 0.3, Vector3.new(CX, FY + 18, CZ), C.portal, Enum.Material.Glass, Workspace)
	r1.Transparency = 0.25
	r1.Reflectance = 0.3
	ringPart = r1

	local r2 = cyl("RotRing2", 14, 0.25, Vector3.new(CX, FY + 24, CZ), C.portalGlow, Enum.Material.Glass, Workspace)
	r2.Transparency = 0.15
	r2.Reflectance = 0.2
	ringPart2 = r2
end

-- ============================================================
-- BUILD (wrapped in pcall for safety)
-- ============================================================

local flickerLights: { PointLight } = {}
local buildOk, buildErr = pcall(function()
buildFloor()
buildPit()
buildParticles()
buildWalls()
flickerLights = buildCeiling()
buildPillars()
buildBridges()
buildTitle()
buildRotatingRings()
buildDesk()
buildDoor()
buildTeleportPads()
buildProps()
-- SpawnLocation inside the lobby
local spawnPart = Instance.new("SpawnLocation")
spawnPart.Name = "LobbySpawn"
spawnPart.Anchored = true
spawnPart.CanCollide = false
spawnPart.Size = Vector3.new(4, 0.5, 4)
spawnPart.Position = Vector3.new(CX, FY + 0.5, CZ + 20)
spawnPart.Neutral = true
spawnPart.Transparency = 1
spawnPart.Parent = lobbyModel

lobbyModel.PrimaryPart = lobbyModel:FindFirstChild("FloorBase") :: BasePart
end) -- pcall build

if buildOk then
	print("[LobbyBuilder] Built " .. partCount .. " parts — THE MAW v2 with portal & rotating rings")
else
	warn("[LobbyBuilder] BUILD FAILED: " .. tostring(buildErr))
	-- Build a fallback floor so players aren't in the void
	pt("FallbackFloor", Vector3.new(50, 0.5, 50), Vector3.new(CX, FY - 0.25, CZ), Color3.fromRGB(60, 58, 65), Enum.Material.Concrete, Workspace)
	lobbyModel.PrimaryPart = lobbyModel:FindFirstChild("FallbackFloor") :: BasePart
end

-- ============================================================
-- SIGNAL LOBBY READY
-- ============================================================

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local eventFolder = ReplicatedStorage:FindFirstChild("BunkerEvents")
if not eventFolder then
	eventFolder = Instance.new("Folder")
	eventFolder.Name = "BunkerEvents"
	eventFolder.Parent = ReplicatedStorage
end
local readyEvent = eventFolder:FindFirstChild("LobbyReady") :: BindableEvent?
if not readyEvent then
	readyEvent = Instance.new("BindableEvent")
	readyEvent.Name = "LobbyReady"
	readyEvent.Parent = eventFolder
end
readyEvent:Fire()
print("=== LobbyBuilder COMPLETE ===")

-- Fix existing spawns and teleport players inside the lobby
local lobbyPos = Vector3.new(CX, FY + 2, CZ + 20)
for _, spawn in Workspace:GetChildren() do
	if spawn:IsA("SpawnLocation") then
		spawn.Position = lobbyPos
		spawn.Neutral = true
	end
end
for _, player in game:GetService("Players"):GetPlayers() do
	local char = player.Character
	if char and char:FindFirstChild("HumanoidRootPart") then
		char.HumanoidRootPart.CFrame = CFrame.new(lobbyPos)
	end
end

-- ============================================================
-- HEARTBEAT — animations
-- ============================================================

local rotationAngle = 0

RunService.Heartbeat:Connect(function(dt: number)
	pcall(function()
	local t = tick()

	-- Fluorescent flicker
	for i, pl in flickerLights do
		if not pl or not pl.Parent then continue end
		local ft = t * (2.5 + i * 0.15)
		local n = math.noise(ft * 3, i * 7, 0)
		local b = 3.5 + n * 1.5
		if math.sin(ft * 0.4 + i * 1.3) > 0.96 then b = 0.2 end
		if math.sin(ft * 0.25 + i * 2.7) > 0.98 then b = 0.4 end
		pl.Brightness = math.max(0.2, b)
	end

	-- Teleporter sign pulse
	for _, label in teleportSigns do
		if label and label.Parent then
			local pulse = 0.6 + math.sin(t * 2.5) * 0.4
			label.TextTransparency = 1 - pulse
		end
	end

	-- Rotating portal rings
	rotationAngle += dt * 0.15
	if ringPart then
		ringPart.CFrame = CFrame.new(ringPart.Position) * CFrame.Angles(0, rotationAngle, 0)
	end
	if ringPart2 then
		ringPart2.CFrame = CFrame.new(ringPart2.Position) * CFrame.Angles(0, -rotationAngle * 1.5, 0)
	end

	-- Abyss glow pulse
	for _, pl in pitLights do
		if pl and pl.Parent then
			local pulse = 4 + math.sin(t * 0.8) * 2
			pl.Brightness = math.max(2.5, pulse)
		end
	end
	end) -- pcall
end)
