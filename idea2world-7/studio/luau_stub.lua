--!nocheck
-- Roblox API simulator used by the Idea2World integration tests and the mock Studio bridge.
-- It executes the *real* generated Luau modules against a stubbed DataModel, so a build either
-- runs end-to-end or fails loudly. It is not a renderer: geometry positions are approximated.

local STUB = {}

---------------------------------------------------------------------------------------------------
-- Vector3 / Vector2
---------------------------------------------------------------------------------------------------
local function vec3(x, y, z)
	local v = { X = x or 0, Y = y or 0, Z = z or 0 }
	return setmetatable(v, {
		__add = function(a, b) return vec3(a.X + b.X, a.Y + b.Y, a.Z + b.Z) end,
		__sub = function(a, b) return vec3(a.X - b.X, a.Y - b.Y, a.Z - b.Z) end,
		__mul = function(a, b)
			if type(a) == "number" then return vec3(a * b.X, a * b.Y, a * b.Z) end
			if type(b) == "number" then return vec3(a.X * b, a.Y * b, a.Z * b) end
			return vec3(a.X * b.X, a.Y * b.Y, a.Z * b.Z)
		end,
		__tostring = function(v) return string.format("(%.1f, %.1f, %.1f)", v.X, v.Y, v.Z) end,
	})
end
STUB.Vector3 = setmetatable({ new = vec3 }, {
	__index = function(_, key) return vec3(0, 0, 0)[key] end,
})
STUB.Vector3.new = vec3
STUB.Vector3.zero = vec3(0, 0, 0)
STUB.Vector3.one = vec3(1, 1, 1)
STUB.Vector2 = { new = function(x, y) return { X = x or 0, Y = y or 0 } end }

---------------------------------------------------------------------------------------------------
-- Color3
---------------------------------------------------------------------------------------------------
local function color3(r, g, b)
	local c = { R = r or 0, G = g or 0, B = b or 0 }
	c.r, c.g, c.b = c.R, c.G, c.B
	return setmetatable(c, {
		__index = {
			Lerp = function(a, b, t)
				return color3(a.R + (b.R - a.R) * t, a.G + (b.G - a.G) * t, a.B + (b.B - a.B) * t)
			end,
		},
		__tostring = function(v) return string.format("rgb(%d,%d,%d)", v.R * 255, v.G * 255, v.B * 255) end,
	})
end
STUB.Color3 = {
	new = color3,
	fromRGB = function(r, g, b) return color3((r or 0) / 255, (g or 0) / 255, (b or 0) / 255) end,
	fromHSV = function() return color3(0.5, 0.5, 0.5) end,
}

---------------------------------------------------------------------------------------------------
-- CFrame (position only + approximate rotation composition)
---------------------------------------------------------------------------------------------------
local cframeMeta = {
	__mul = function(a, b)
		local p = vec3(a.Position.X + b.Position.X, a.Position.Y + b.Position.Y, a.Position.Z + b.Position.Z)
		return cframe(p, { a._rot[1] + b._rot[1], a._rot[2] + b._rot[2], a._rot[3] + b._rot[3] })
	end,
	__index = {
		Inverse = function(self) return cframe(vec3(-self.Position.X, -self.Position.Y, -self.Position.Z)) end,
	},
}

function cframe(pos, rot)
	return setmetatable({ Position = pos or vec3(0, 0, 0), _rot = rot or { 0, 0, 0 } }, cframeMeta)
end

STUB.CFrame = {
	new = function(a, b, c)
		if type(a) == "table" and a.X then return cframe(a) end
		if a == nil then return cframe(vec3(0, 0, 0)) end
		return cframe(vec3(a, b, c))
	end,
	Angles = function(rx, ry, rz) return cframe(vec3(0, 0, 0), { rx or 0, ry or 0, rz or 0 }) end,
	fromEulerAnglesXYZ = function(rx, ry, rz) return cframe(vec3(0, 0, 0), { rx or 0, ry or 0, rz or 0 }) end,
	lookAt = function(a) return cframe(a or vec3(0, 0, 0)) end,
	Identity = cframe(vec3(0, 0, 0)),
}

---------------------------------------------------------------------------------------------------
-- Enum
---------------------------------------------------------------------------------------------------
local enumItemMeta = {
	__tostring = function(self) return self.Name end,
}
local function enumItem(name, value)
	return setmetatable({ Name = name, Value = value or 0, EnumType = name }, enumItemMeta)
end
STUB.Enum = setmetatable({}, {
	__index = function(_, enumName)
		return setmetatable({}, {
			__index = function(_, itemName)
				return enumItem(itemName, 0)
			end,
		})
	end,
})

STUB.UDim2 = { fromScale = function(x, y) return { X = x, Y = y, Scale = true } end,
	new = function(x, y, z, w) return { X = x, Y = y, Z = z or 0, W = w or 0 } end }
STUB.UDim = { new = function(x) return { Offset = x } end }
STUB.NumberRange = { new = function(a, b) return { Min = a, Max = b or a } end }
STUB.NumberSequenceKeypoint = { new = function(t, v) return { Time = t, Value = v } end }
STUB.NumberSequence = { new = function(v) return { keypoints = v } end }
STUB.ColorSequence = { new = function(v) return { keypoints = v } end }
STUB.ColorSequenceKeypoint = { new = function(t, v) return { Time = t, Value = v } end }
STUB.RaycastParams = { new = function() return { FilterDescendantsInstances = {} } end }
STUB.Random = { new = function(seed) return { NextNumber = function() return 0.5 end, NextInteger = function(_, a) return a end } end }
STUB.TweenInfo = { new = function() return {} end }
STUB.CornerRadius = { new = function(p) return { Pixels = p or 0 } end }
STUB.DateTime = { now = function() return { ToIsoDate = function() return "2026-01-01T00:00:00Z" end } end }

---------------------------------------------------------------------------------------------------
-- Instance tree
---------------------------------------------------------------------------------------------------
local CLASS_PARENTS = {
	Instance = nil,
	BasePart = "Instance",
	Part = "BasePart",
	WedgePart = "BasePart",
	CornerWedgePart = "BasePart",
	MeshPart = "BasePart",
	SpawnLocation = "Part",
	Model = "Instance",
	Folder = "Instance",
	ModuleScript = "Instance",
	Script = "Instance",
	Sound = "Instance",
	SoundGroup = "Instance",
	PointLight = "Instance",
	SpotLight = "Instance",
	ParticleEmitter = "Instance",
	BillboardGui = "Instance",
	SurfaceGui = "Instance",
	TextLabel = "Instance",
	TextButton = "Instance",
	ProximityPrompt = "Instance",
	Atmosphere = "Instance",
	BloomEffect = "Instance",
	ColorCorrectionEffect = "Instance",
	SunRaysEffect = "Instance",
	Terrain = "Instance",
	WorldModel = "Instance",
}

local function ancestorChain(className)
	local chain, current = {}, className
	while current do
		table.insert(chain, current)
		current = CLASS_PARENTS[current]
	end
	return chain
end

local instanceCounts = {}
local function newInstance(className)
	local class = className or "Instance"
	local self = {
		ClassName = class,
		Name = class,
		_children = {},
		_attrs = {},
		_parent = nil,
	}
	instanceCounts[class] = (instanceCounts[class] or 0) + 1

	local methods = {}
	function methods:IsA(query)
		for _, name in ipairs(ancestorChain(self.ClassName)) do
			if name == query then return true end
		end
		return false
	end
	function methods:FindFirstChild(name)
		for _, child in ipairs(self._children) do
			if child.Name == name then return child end
		end
		return nil
	end
	function methods:FindFirstChildOfClass(class)
		for _, child in ipairs(self._children) do
			if child.ClassName == class then return child end
		end
		return nil
	end
	function methods:FindFirstChildWhichIsA(class)
		for _, child in ipairs(self._children) do
			if child:IsA(class) then return child end
		end
		return nil
	end
	function methods:WaitForChild(name)
		return self:FindFirstChild(name)
	end
	function methods:GetChildren()
		local out = {}
		for i, child in ipairs(self._children) do out[i] = child end
		return out
	end
	function methods:GetDescendants()
		local out = {}
		for _, child in ipairs(self._children) do
			table.insert(out, child)
			for _, descendant in ipairs(child:GetDescendants()) do
				table.insert(out, descendant)
			end
		end
		return out
	end
	function methods:SetAttribute(key, value) self._attrs[key] = value end
	function methods:GetAttribute(key) return self._attrs[key] end
	function methods:GetAttributes() return self._attrs end
	function methods:Destroy()
		local parent = self._parent
		if parent then
			for i, child in ipairs(parent._children) do
				if child == self then
					table.remove(parent._children, i)
					break
				end
			end
		end
		self._parent = nil
	end
	function methods:ClearAllChildren()
		for _, child in ipairs(self._children) do child._parent = nil end
		self._children = {}
	end
	function methods:Clone()
		local copy = newInstance(self.ClassName)
		for key, value in pairs(self) do
			if key ~= "_children" and key ~= "_parent" and key ~= "ClassName" and key ~= "_attrs" then
				copy[key] = value
			end
		end
		for key, value in pairs(self._attrs) do copy._attrs[key] = value end
		for _, child in ipairs(self._children) do
			local childCopy = child:Clone()
			childCopy._parent = copy
			table.insert(copy._children, childCopy)
		end
		return copy
	end
	function methods:PivotTo(target)
		for _, part in ipairs(self:GetDescendants()) do
			if part:IsA("BasePart") then
				part.CFrame = target
			end
		end
		if self:IsA("BasePart") then self.CFrame = target end
	end
	function methods:ScaleTo(scale)
		for _, part in ipairs(self:GetDescendants()) do
			if part:IsA("BasePart") and part.Size then
				part.Size = vec3(part.Size.X * scale, part.Size.Y * scale, part.Size.Z * scale)
			end
		end
	end
	function methods:GetPivot()
		return self.CFrame or cframe(vec3(0, 0, 0))
	end
	function methods:Play() self._playing = true end
	function methods:Stop() self._playing = false end
	function methods:SetPrimaryPartCFrame(target) self:PivotTo(target) end

	-- ---- Idea2World 7.0 UI additions (additive; world modules never call these) -------
	local function eventObj(t, key)
		local obj = rawget(t, "_ev_" .. key)
		if not obj then
			obj = {}
			obj._listeners = {}
			function obj:Connect(fn)
				table.insert(obj._listeners, fn)
				return function() end
			end
			rawset(t, "_ev_" .. key, obj)
		end
		return obj
	end
	function methods:Create()
		return { Play = function() end }
	end
	function methods:OnClientEvent()
		return eventObj(self, "OnClientEvent")
	end
	function methods:OnServerEvent()
		return eventObj(self, "OnServerEvent")
	end
	-- Real Roblox semantics: client handlers get (args...); server handlers get (player, args...).
	function methods:FireClient(_target, ...)
		local obj = rawget(self, "_ev_OnClientEvent")
		if not obj then return end
		for _, fn in ipairs(obj._listeners) do
			local ok, err = pcall(fn, ...)
			if not ok then print("[ui] handler error: " .. tostring(err)) end
		end
	end
	function methods:FireServer(...)
		local obj = rawget(self, "_ev_OnServerEvent")
		if obj then
			local player = rawget(STUB, "_currentPlayer")
			for _, fn in ipairs(obj._listeners) do
				local ok, err = pcall(fn, player, ...)
				if not ok then print("[ui] server handler error: " .. tostring(err)) end
			end
		end
		if STUB._serverQueue then
			table.insert(STUB._serverQueue, { from = self, args = { ... } })
		end
	end

	local proxy = setmetatable(self, {
		__index = function(t, key)
			if key == "Parent" then return t._parent end
			-- Roblox remote events are properties that return an event object, not methods.
			if key == "OnClientEvent" or key == "OnServerEvent" then
				return eventObj(t, key)
			end
			-- Common UI/input events the generated UI wires up (all return a connectable event).
			local uiEvents = {
				MouseButton1Click = true, MouseButton2Click = true, MouseButton1Down = true,
				MouseButton1Up = true, MouseButton2Down = true, MouseEnter = true, MouseLeave = true,
				Tapped = true, Triggered = true, Changed = true, InputBegan = true, InputEnded = true,
			}
			if uiEvents[key] then
				return eventObj(t, key)
			end
			local method = methods[key]
			if method then return method end
			for _, child in ipairs(t._children) do
				if child.Name == key then return child end
			end
			return rawget(t, key)
		end,
		__newindex = function(t, key, value)
			if key == "Parent" then
				if t._parent then
					for i, child in ipairs(t._parent._children) do
						if child == t then table.remove(t._parent._children, i); break end
					end
				end
				t._parent = value
				if value then table.insert(value._children, t) end
				return
			end
			if key == "CFrame" then
				rawset(t, "CFrame", value)
				rawset(t, "Position", value.Position or vec3(0, 0, 0))
				return
			end
			if key == "Position" then
				rawset(t, "Position", value)
				rawset(t, "CFrame", cframe(value))
				return
			end
			if key == "Size" then
				rawset(t, "Size", value)
				return
			end
			rawset(t, key, value)
		end,
	})
	if self.ClassName == "BasePart" or ancestorChain(class)[2] == "BasePart" then
		self.Size = vec3(1, 1, 1)
		self.CFrame = cframe(vec3(0, 0, 0))
		self.Position = vec3(0, 0, 0)
		self.Color = color3(0.5, 0.5, 0.5)
		self.Transparency = 0
		self.CanCollide = true
		self.Anchored = false
		self.Material = enumItem("Plastic")
	end
	if class == "ProximityPrompt" then
		self.Triggered = { Connect = function(_, fn) self._triggered = fn end }
	end
	return proxy
end

STUB.newInstance = newInstance
STUB.Instance = { new = function(className, parent)
	local inst = newInstance(className)
	if parent then inst.Parent = parent end
	return inst
end }

---------------------------------------------------------------------------------------------------
-- Services and workspace
---------------------------------------------------------------------------------------------------
local services = {}
local function service(name)
	if services[name] then return services[name] end
	local svc = newInstance("Instance")
	svc.Name = name
	svc.ClassName = name
	services[name] = svc
	if name == "Players" then
		local players = {}
		function svc:GetPlayers()
			local out = {}
			for i, p in ipairs(players) do out[i] = p end
			return out
		end
		svc.PlayerAdded = { Connect = function(_, fn)
			for _, p in ipairs(players) do fn(p) end
			return function() end
		end }
		svc._players = players
	end
	return svc
end

local terrain = newInstance("Terrain")
terrain.Name = "Terrain"
STUB.terrainFillCalls = 0
STUB.terrainWaterCalls = 0
function terrain:FillBlock(cf, size, material)
	STUB.terrainFillCalls += 1
	STUB.lastTerrainSize = size
end
function terrain:FillCylinder() STUB.terrainFillCalls += 1 end
function terrain:FillRegion() STUB.terrainFillCalls += 1 end

local workspaceStub = newInstance("Folder")
workspaceStub.Name = "Workspace"
workspaceStub.Terrain = terrain
STUB.workspace = workspaceStub
function workspaceStub:Raycast()
	return nil
end

STUB.game = {
	GetService = function(_, name)
		if name == "Workspace" then return workspaceStub end
		return service(name)
	end,
	FindService = function(_, name) return services[name] end,
}

STUB.task = {
	wait = function() return 0 end,
	spawn = function(fn) fn() end,
	defer = function(fn) fn() end,
	delay = function(_, fn) fn() end,
	cancel = function() end,
}

STUB.typeof = function(value)
	if type(value) == "table" then
		if value.ClassName then return "Instance" end
		if value.X and value.Y then return "Vector3" end
		if value.R and value.G then return "Color3" end
		if value.Position then return "CFrame" end
	end
	return type(value)
end

---------------------------------------------------------------------------------------------------
-- JSON encoder for the build report
---------------------------------------------------------------------------------------------------
local function encode(value)
	local t = type(value)
	if t == "nil" then return "null" end
	if t == "boolean" then return tostring(value) end
	if t == "number" then
		if value ~= value or value == math.huge or value == -math.huge then return "null" end
		return string.format("%.4f", value)
	end
	if t == "string" then
		return '"' .. value:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n'):gsub('\t', '\\t') .. '"'
	end
	if t == "table" then
		if #value > 0 then
			local items = {}
			for _, item in ipairs(value) do table.insert(items, encode(item)) end
			return "[" .. table.concat(items, ",") .. "]"
		end
		local keys = {}
		for key in pairs(value) do
			if type(key) == "string" or type(key) == "number" then table.insert(keys, key) end
		end
		table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)
		local items = {}
		for _, key in ipairs(keys) do
			table.insert(items, '"' .. tostring(key) .. '":' .. encode(value[key]))
		end
		return "{" .. table.concat(items, ",") .. "}"
	end
	return "null"
end

STUB.encode = encode
STUB.instanceCounts = instanceCounts
STUB.services = services
STUB.withCFrameMeta = function(cf) return cf end
STUB.vec3 = vec3
STUB.color3 = color3
return STUB
