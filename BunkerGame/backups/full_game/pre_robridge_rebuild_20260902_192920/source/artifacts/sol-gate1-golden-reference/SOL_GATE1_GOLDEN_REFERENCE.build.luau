-- SOL Gate 1 Golden Reference v28
-- NON-PRODUCTION, UNMAPPED ARTIFACT. Reconstructs the isolated review candidate.
local Workspace = game:GetService("Workspace")
local Terrain = Workspace.Terrain
local ROOT_NAME = "SOL_GATE1_GOLDEN_REFERENCE"
local REGION_MIN, REGION_MAX = Vector3.new(780, 20, -80), Vector3.new(980, 110, 120)
local VOXEL = 4

assert(not Workspace:FindFirstChild(ROOT_NAME), ROOT_NAME .. " already exists; refusing to overwrite it")
local function overlaps(part: BasePart): boolean
	local half = part.Size * 0.5
	local lo, hi = part.Position - half, part.Position + half
	return lo.X <= REGION_MAX.X and hi.X >= REGION_MIN.X and lo.Y <= REGION_MAX.Y
		and hi.Y >= REGION_MIN.Y and lo.Z <= REGION_MAX.Z and hi.Z >= REGION_MIN.Z
end
local gameWorld = Workspace:FindFirstChild("GameWorld")
if gameWorld then
	for _, item in gameWorld:GetDescendants() do
		if item:IsA("BasePart") then
			assert(not overlaps(item), "GameWorld overlaps Golden Reference region at " .. item:GetFullName())
		end
	end
end

local routeXZ = {
	Vector2.new(805, -62), Vector2.new(825, -28), Vector2.new(875, -20),
	Vector2.new(930, -15), Vector2.new(946, -4), Vector2.new(930, 23),
}
local function smoothstep(a: number, b: number, value: number): number
	local t = math.clamp((value - a) / (b - a), 0, 1)
	return t * t * (3 - 2 * t)
end
local function routeDistance(point: Vector2): (number, number)
	local best, bestIndex = math.huge, 1
	for index = 1, #routeXZ - 1 do
		local a, segment = routeXZ[index], routeXZ[index + 1] - routeXZ[index]
		local t = math.clamp((point - a):Dot(segment) / segment:Dot(segment), 0, 1)
		local distance = (point - (a + segment * t)).Magnitude
		if distance < best then best, bestIndex = distance, index end
	end
	return best, bestIndex
end
local function geologicalHeight(x: number, z: number): number
	local northRise = 6 * smoothstep(-50, 70, z)
	local westShoulder = 3 * math.exp(-(((x - 860) / 58) ^ 2 + ((z - 20) / 72) ^ 2))
	local burialMass = 7 * math.exp(-(((x - 928) / 44) ^ 2 + ((z - 38) / 48) ^ 2))
	local rearRidge = 6 * math.exp(-(((x - 910) / 82) ^ 2 + ((z - 80) / 48) ^ 2))
	local eastCounterspace = -1.5 * math.exp(-(((x - 970) / 32) ^ 2 + ((z - 5) / 48) ^ 2))
	local undulation = .55 * math.sin((x + z) * .035)
	return 58 + northRise + westShoulder + burialMass + rearRidge + eastCounterspace + undulation
end

local region = Region3.new(REGION_MIN, REGION_MAX):ExpandToGrid(VOXEL)
local materials, occupancy = Terrain:ReadVoxels(region, VOXEL)
local regionMin = region.CFrame.Position - region.Size / 2
for ix = 1, materials.Size.X do
	for iy = 1, materials.Size.Y do
		for iz = 1, materials.Size.Z do
			local x = regionMin.X + (ix - 0.5) * VOXEL
			local y = regionMin.Y + (iy - 0.5) * VOXEL
			local z = regionMin.Z + (iz - 0.5) * VOXEL
			local distance, segment = routeDistance(Vector2.new(x, z))
			local height = geologicalHeight(x, z)
			if segment < 5 or z < 12 then
				local routeHeight = 54.5 + 0.025 * math.clamp(z + 20, 0, 32)
				height += (routeHeight - height) * (1 - smoothstep(5.5, 14, distance))
			end
			local patch = math.sin(x * 0.083) + math.sin(z * 0.137) + 0.65 * math.sin((x + z) * 0.041)
			local material = Enum.Material.Ground
			if x >= 919 and x <= 941 and z >= 16 and z <= 42 then
				material = if math.abs(x - 930) < 7 and z < 38 then Enum.Material.Mud else Enum.Material.Ground
			elseif distance < 6.8 and z <= 26 then material = Enum.Material.Mud
			elseif patch > -0.18 and z > -38 then material = Enum.Material.Grass
			elseif z > 8 and math.abs(x - 930) < 48 and patch < -0.95 then material = Enum.Material.Rock end
			if y <= height then
				occupancy[ix][iy][iz] = math.clamp((height - (y - VOXEL / 2)) / VOXEL, 0, 1)
				materials[ix][iy][iz] = if y >= height - VOXEL then material else Enum.Material.Ground
			else
				occupancy[ix][iy][iz], materials[ix][iy][iz] = 0, Enum.Material.Air
			end
		end
	end
end
Terrain:WriteVoxels(region, VOXEL, materials, occupancy)

-- Broaden only the final approach into an open-air valley. This prevents the
-- approved reveal camera from reading as a tunnel while preserving high shoulders.
local openRegion = Region3.new(Vector3.new(906, 52, -18), Vector3.new(972, 88, 28)):ExpandToGrid(VOXEL)
local openMaterials, openOccupancy = Terrain:ReadVoxels(openRegion, VOXEL)
local openMin = openRegion.CFrame.Position - openRegion.Size / 2
local finalRoute = { Vector2.new(930, -15), Vector2.new(946, -4), Vector2.new(930, 23) }
local function segmentDistance(point: Vector2, a: Vector2, b: Vector2): number
	local segment = b - a
	local t = math.clamp((point - a):Dot(segment) / segment:Dot(segment), 0, 1)
	return (point - (a + segment * t)).Magnitude
end
for ix = 1, openMaterials.Size.X do
	for iy = 1, openMaterials.Size.Y do
		for iz = 1, openMaterials.Size.Z do
			local x = openMin.X + (ix - .5) * VOXEL
			local y = openMin.Y + (iy - .5) * VOXEL
			local z = openMin.Z + (iz - .5) * VOXEL
			local point = Vector2.new(x, z)
			local distance = math.min(
				segmentDistance(point, finalRoute[1], finalRoute[2]),
				segmentDistance(point, finalRoute[2], finalRoute[3])
			)
			local width = if z < 10 then 25 else 21
			local target = 55.3 + .12 * distance + .018 * distance * distance
			if distance < width and z <= 24 and y > target then
				openMaterials[ix][iy][iz], openOccupancy[ix][iy][iz] = Enum.Material.Air, 0
			end
		end
	end
end
Terrain:WriteVoxels(openRegion, VOXEL, openMaterials, openOccupancy)

-- Bounded entrance void; continuous earth remains above and around the opening.
local cut = Region3.new(Vector3.new(912, 52, 10), Vector3.new(952, 76, 42)):ExpandToGrid(VOXEL)
local cutMaterials, cutOccupancy = Terrain:ReadVoxels(cut, VOXEL)
local cutMin = cut.CFrame.Position - cut.Size / 2
for ix = 1, cutMaterials.Size.X do
	for iy = 1, cutMaterials.Size.Y do
		for iz = 1, cutMaterials.Size.Z do
			local x = cutMin.X + (ix - 0.5) * VOXEL
			local y = cutMin.Y + (iy - 0.5) * VOXEL
			local z = cutMin.Z + (iz - 0.5) * VOXEL
			local t = math.clamp((z - 10) / 16, 0, 1)
			local centerX = if z > 26 then 930 else 940 + (930 - 940) * t
			local halfWidth, top = 11 - 2 * t, 65.5 + 1.5 * t
			if z >= 10 and z <= 40 and math.abs(x - centerX) <= halfWidth and y > 54 and y <= top then
				cutMaterials[ix][iy][iz], cutOccupancy[ix][iy][iz] = Enum.Material.Air, 0
			end
		end
	end
end
Terrain:WriteVoxels(cut, VOXEL, cutMaterials, cutOccupancy)

local function carveRetainingContact(minimum: Vector3, maximum: Vector3, outer: Vector2, inner: Vector2)
	local contactRegion = Region3.new(minimum, maximum):ExpandToGrid(VOXEL)
	local contactMaterials, contactOccupancy = Terrain:ReadVoxels(contactRegion, VOXEL)
	local contactMin = contactRegion.CFrame.Position - contactRegion.Size / 2
	local segment = inner - outer
	for ix = 1, contactMaterials.Size.X do
		for iy = 1, contactMaterials.Size.Y do
			for iz = 1, contactMaterials.Size.Z do
				local x = contactMin.X + (ix - .5) * VOXEL
				local y = contactMin.Y + (iy - .5) * VOXEL
				local z = contactMin.Z + (iz - .5) * VOXEL
				local point = Vector2.new(x, z)
				local t = math.clamp((point - outer):Dot(segment) / segment:Dot(segment), 0, 1)
				local distance = (point - (outer + segment * t)).Magnitude
				local top = 58.2 + 7.1 * t
				if distance <= 4.2 and y > 54 and y <= top then
					contactMaterials[ix][iy][iz], contactOccupancy[ix][iy][iz] = Enum.Material.Air, 0
				end
			end
		end
	end
	Terrain:WriteVoxels(contactRegion, VOXEL, contactMaterials, contactOccupancy)
end

-- Restrained engineered cuts expose structural contact while preserving the ridge.
carveRetainingContact(
	Vector3.new(906, 52, 12),
	Vector3.new(926, 68, 34),
	Vector2.new(912.2, 18.8),
	Vector2.new(921.5, 28.8)
)
carveRetainingContact(
	Vector3.new(934, 52, 10),
	Vector3.new(954, 70, 34),
	Vector2.new(949, 14.5),
	Vector2.new(938.4, 28.5)
)

-- The deep bounded void is concealed by the structural portal and retained overburden.
Terrain:FillBlock(CFrame.new(930, 59, 40), Vector3.new(21, 9, 26), Enum.Material.Air)

local root = Instance.new("Model")
root.Name, root.Parent = ROOT_NAME, Workspace
root:SetAttribute("NonProduction", true)
root:SetAttribute("Purpose", "Gate 1 spatial language teaching reference")
root:SetAttribute("RegionMin", "780,20,-80")
root:SetAttribute("RegionMax", "980,110,120")
root:SetAttribute("ReferenceVersion", "v36-focused-reveal-candidate")
root:SetAttribute("FinalVisualReview", "SOL_PASS")
root:SetAttribute("GeologyMethod", "Single analytic heightfield plus bounded entrance void")
root:SetAttribute("SurfaceLanguage", "Exposed damp ground and rock with irregular grass clumps")
root:SetAttribute("RouteSurfaceWidth", "13.6 stud mud core; irregular grass and ground shoulders")
root:SetAttribute("ScaleLanguage", "Player-height cameras and 8-stud fortified aperture; proxy retired")
root:SetAttribute("RevealArchitecture", "Asymmetric load-bearing portal, compact retaining cheek, descending layered entry")
root:SetAttribute("InteriorVoid", "21x9x26 bounded behind structural portal")
local metadata = Instance.new("Folder")
metadata.Name, metadata.Parent = "REFERENCE_METADATA", root
local status = Instance.new("StringValue")
status.Name, status.Value, status.Parent = "STATUS", "SOL GOLDEN REFERENCE - NON PRODUCTION - HUMAN REVIEW CANDIDATE", metadata
local origin = Instance.new("Part")
origin.Name, origin.Size, origin.CFrame = "REFERENCE_ORIGIN", Vector3.one, CFrame.new(900, 54.5, 0)
origin.Anchored, origin.CanCollide, origin.CanQuery, origin.Transparency, origin.Parent = true, false, false, 1, root

local function part(parent: Instance, name: string, size: Vector3, cframe: CFrame, material: Enum.Material, color: Color3): Part
	local item = Instance.new("Part")
	item.Name, item.Size, item.CFrame = name, size, cframe
	item.Anchored, item.Material, item.Color = true, material, color
	item.TopSurface, item.BottomSurface, item.Parent = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth, parent
	return item
end
local route = Instance.new("Model")
route.Name, route.Parent = "PLAYER_APPROACH_DOGLEG", root
route:SetAttribute("TeachingBeat", "Indirect approach, lateral dogleg, terrain-held occlusion, late reveal")
route:SetAttribute("RoutePoints", "805,-62 > 825,-28 > 875,-20 > 930,-15 > 946,-4 > 930,23")
route:SetAttribute("Implementation", "Terrain elevation and material only; no overlaid path parts")
local bunker = Instance.new("Model")
bunker.Name, bunker.Parent = "BUNKER_ENTRANCE_CUT", root
bunker:SetAttribute("TeachingBeat", "Deep fortified portal under retained overburden with asymmetric engineered retaining cut")
local concrete = Color3.fromRGB(105, 108, 102)
part(bunker, "Threshold", Vector3.new(15, .5, 15), CFrame.new(930, 55.15, 34), Enum.Material.Concrete, Color3.fromRGB(67, 70, 66))
part(bunker, "WestJamb", Vector3.new(4.2, 9.6, 9), CFrame.new(921.1, 59.8, 29.5), Enum.Material.Concrete, concrete)
part(bunker, "EastJamb", Vector3.new(2.6, 9, 8), CFrame.new(938.2, 59.55, 29.5), Enum.Material.Concrete, concrete)
part(bunker, "Lintel", Vector3.new(20.5, 3.2, 4.4), CFrame.new(929.6, 64.8, 27.3), Enum.Material.Concrete, concrete)
part(bunker, "BuriedCeiling", Vector3.new(14, 1.2, 18), CFrame.new(930, 64, 37), Enum.Material.Concrete, Color3.fromRGB(80, 84, 80))
part(bunker, "RecessShadow", Vector3.new(13.4, 8.4, 1), CFrame.new(930, 59.15, 48.5), Enum.Material.SmoothPlastic, Color3.fromRGB(3, 5, 5))
part(bunker, "WestInnerReveal", Vector3.new(1.1, 8.3, 17), CFrame.new(923.85, 59.3, 40), Enum.Material.Concrete, Color3.fromRGB(67, 72, 69))
part(bunker, "EastInnerReveal", Vector3.new(1.1, 8.3, 17), CFrame.new(936.15, 59.3, 40), Enum.Material.Concrete, Color3.fromRGB(67, 72, 69))
part(bunker, "InnerCompressionBeam", Vector3.new(13.3, 1.3, 1.8), CFrame.new(930, 62.8, 36.5), Enum.Material.Concrete, Color3.fromRGB(61, 66, 63))
part(bunker, "DescendingEntrySlab", Vector3.new(12.1, .45, 20), CFrame.new(930, 54.55, 40) * CFrame.Angles(math.rad(4), 0, 0), Enum.Material.Concrete, Color3.fromRGB(43, 48, 46))
local retaining = Instance.new("WedgePart")
retaining.Name = "AsymmetricRetainingWing"
retaining.Size = Vector3.new(2.6, 7.4, (Vector3.new(938.7, 58.8, 29) - Vector3.new(943.2, 57.5, 21.7)).Magnitude)
retaining.CFrame = CFrame.lookAt(
	(Vector3.new(938.7, 58.8, 29) + Vector3.new(943.2, 57.5, 21.7)) / 2,
	Vector3.new(943.2, 57.5, 21.7)
)
retaining.Anchored = true
retaining.Material = Enum.Material.Concrete
retaining.Color = Color3.fromRGB(86, 91, 86)
retaining.TopSurface, retaining.BottomSurface, retaining.Parent = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth, bunker

local trees = Instance.new("Model")
trees.Name, trees.Parent = "CREEPY_TREE_SILHOUETTES", root
trees:SetAttribute("Purpose", "Asymmetric foreground framing and sparse ridge rhythm; not vegetation dressing")
local PINE_MESH = Content.fromUri("rbxassetid://116631823794510")
local SCRUB_MESH = Content.fromUri("rbxassetid://112795904656087")
local specs = {
	{ "Approach_Left_01", 792, -48, .95, 1.82, .95, -28, -3, false },
	{ "Approach_Left_02", 801, -19, 1.08, 2.02, 1, 34, 2, false },
	{ "Shoulder_01", 846, -4, 1, 1.72, .9, -12, -2, false },
	{ "Shoulder_02", 861, 8, .88, 1.48, .92, 51, 3, false },
	{ "RearRidge_01", 908, 53, .95, 1.92, .9, 23, 2, false },
	{ "RearRidge_02", 930, 61, 1.18, 2.18, 1.1, -17, -3, false },
	{ "EastCounter_01", 959, 38, .9, 1.68, .95, 46, 2, false },
	{ "Reveal_Frame_01", 970, 4, 1.04, 1.88, 1, -32, -2, false },
	{ "RidgeScrub_01", 874, 38, .9, 1.18, .9, 18, 1, true },
	{ "RidgeScrub_02", 948, 58, 1.1, 1.3, 1, -24, -1, true },
}
local raycastParams = RaycastParams.new()
raycastParams.FilterType = Enum.RaycastFilterType.Exclude
raycastParams.FilterDescendantsInstances = { root }
for _, spec in specs do
	local name, x, z, sx, sy, sz, yaw, lean, scrub = table.unpack(spec)
	local tree = game:GetService("AssetService"):CreateMeshPartAsync(if scrub then SCRUB_MESH else PINE_MESH, {
		CollisionFidelity = Enum.CollisionFidelity.Default,
		RenderFidelity = Enum.RenderFidelity.Automatic,
	})
	tree.Name = name
	tree.Size = Vector3.new(tree.Size.X * sx, tree.Size.Y * sy, tree.Size.Z * sz)
	tree.Anchored, tree.CanCollide, tree.CanQuery, tree.CastShadow = true, false, false, true
	tree.Color = Color3.fromRGB(92, 98, 88)
	local hit = Workspace:Raycast(Vector3.new(x, 120, z), Vector3.new(0, -140, 0), raycastParams)
	assert(hit, "No terrain below tree " .. name)
	local y = hit.Position.Y + tree.Size.Y / 2 - .45
	tree.CFrame = CFrame.new(x, y, z) * CFrame.Angles(math.rad(lean), math.rad(yaw), math.rad(lean * .45))
	tree.Parent = trees
end
return root
