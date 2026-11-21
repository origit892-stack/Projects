-- MapValidator: post-build structural checks inside the real Studio session.
-- Python already validated the plan; this validates what actually got created.
local Config = require(script.Parent.MapConfig)
local WorldLayout = require(script.Parent.WorldLayout)

local MapValidator = {}

local function countDescendants(root: Instance): (number, number)
	local parts, models = 0, 0
	for _, descendant in ipairs(root:GetDescendants()) do
		if descendant:IsA("BasePart") then
			parts += 1
		elseif descendant:IsA("Model") then
			models += 1
		end
	end
	return parts, models
end

function MapValidator.validate(root)
	local checks = {}
	local function add(name, ok, detail)
		table.insert(checks, { name = name, ok = ok, detail = detail })
	end

	local parts, models = countDescendants(root)
	local budget = Config.Budget or {}
	add("instance_budget", parts <= (budget.maxInstances or 14000),
		("parts %d / limit %d"):format(parts, budget.maxInstances or 14000))

	local landmarks = root:FindFirstChild("Landmarks")
	local missing = {}
	local found = 0
	if landmarks then
		for _, poi in ipairs(Config.Pois) do
			local match = nil
			for _, model in ipairs(landmarks:GetDescendants()) do
				if model:IsA("Model") and model:GetAttribute("PoiId") == poi.id then
					match = model
					break
				end
			end
			if match then
				found += 1
			else
				table.insert(missing, poi.name)
			end
		end
	end
	add("landmark_coverage", #missing == 0,
		#missing == 0 and ("%d/%d landmarks built"):format(found, #Config.Pois)
			or ("missing: " .. table.concat(missing, ", ")))

	local spawnLocation = nil
	for _, descendant in ipairs(workspace:GetDescendants()) do
		if descendant:IsA("SpawnLocation") and descendant:GetAttribute("SpawnId") then
			spawnLocation = descendant
			break
		end
	end
	add("spawn_present", spawnLocation ~= nil, spawnLocation and "spawn located" or "no SpawnLocation found")

	-- Floating structure check: sample landmark primary parts and measure the drop to terrain.
	local floating = {}
	if landmarks then
		local params = RaycastParams.new()
		params.FilterType = Enum.RaycastFilterType.Include
		params.FilterDescendantsInstances = { workspace.Terrain }
		for _, model in ipairs(landmarks:GetDescendants()) do
			if model:IsA("Model") and model.PrimaryPart and model:GetAttribute("PoiKind") then
				local kind = model:GetAttribute("PoiKind")
				if kind ~= "bridge" and kind ~= "dock" and kind ~= "portal" and kind ~= "observatory" then
					local origin = model.PrimaryPart.Position
					local result = workspace:Raycast(origin, Vector3.new(0, -120, 0), params)
					if result and result.Distance > 40 then
						table.insert(floating, model.Name)
					end
				end
			end
		end
	end
	add("no_floating_landmarks", #floating == 0,
		#floating == 0 and "all sampled landmarks sit on terrain"
			or ("floating: " .. table.concat(floating, ", ")))

	local emitters = 0
	for _, descendant in ipairs(root:GetDescendants()) do
		if descendant:IsA("ParticleEmitter") then
			emitters += 1
		end
	end
	add("vfx_budget", emitters <= (budget.maxParticleEmitters or 36),
		("emitters %d / limit %d"):format(emitters, budget.maxParticleEmitters or 36))

	local paths = root:FindFirstChild("Paths")
	local pathParts = 0
	if paths then
		pathParts = #paths:GetDescendants()
	end
	add("routes_built", pathParts > 0, ("%d route objects"):format(pathParts))

	if spawnLocation then
		local groundY = WorldLayout.heightAt(spawnLocation.Position.X, spawnLocation.Position.Z)
		add("spawn_height", math.abs(spawnLocation.Position.Y - groundY) < 24,
			("spawn y %.1f vs ground %.1f"):format(spawnLocation.Position.Y, groundY))
	end

	local passed = true
	local failures = {}
	for _, check in ipairs(checks) do
		if not check.ok then
			passed = false
			table.insert(failures, check.name)
		end
	end
	return {
		passed = passed,
		checks = checks,
		failures = failures,
		stats = { parts = parts, models = models, emitters = emitters },
	}
end

return MapValidator
