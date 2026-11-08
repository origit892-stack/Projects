--!strict
local RunService = game:GetService("RunService")

local discoBall = script.Parent
assert(discoBall:IsA("BasePart"), "DiscoScript must be parented to a Part")

local ROTATION_SPEED = 2
local COLOR_CYCLE_SPEED = 0.5

local colors = {
	Color3.fromRGB(255, 0, 0),
	Color3.fromRGB(255, 127, 0),
	Color3.fromRGB(255, 255, 0),
	Color3.fromRGB(0, 255, 0),
	Color3.fromRGB(0, 255, 255),
	Color3.fromRGB(0, 0, 255),
	Color3.fromRGB(127, 0, 255),
	Color3.fromRGB(255, 0, 255),
}

local lights = {}
for _, child in discoBall:GetChildren() do
	if child:IsA("PointLight") then
		table.insert(lights, child)
	end
end

for i, light in lights do
	light.Color = colors[((i - 1) % #colors) + 1]
	light.Brightness = 3
	light.Range = 60
	light.Enabled = true
end

local time = 0

RunService.Heartbeat:Connect(function(dt: number)
	time += dt

	discoBall.CFrame = discoBall.CFrame * CFrame.Angles(0, math.rad(ROTATION_SPEED * 60 * dt), 0)

	for i, light in lights do
		local colorIndex = ((time * COLOR_CYCLE_SPEED * #colors) + i) % #colors
		local idx = math.floor(colorIndex) + 1
		if idx > #colors then
			idx = 1
		end
		light.Color = colors[idx]
	end
end)
