-- Ammo Crate Server Script
local crate = script.Parent
local lid = crate:FindFirstChild("Lid")

local success, err = pcall(function()
	local prompt = Instance.new("ProximityPrompt")

	prompt.Name = "OpenCratePrompt"
	prompt.ActionText = "Open"
	prompt.KeyboardKeyCode = Enum.KeyCode.E
	prompt.HoldDuration = 1
	prompt.Parent = crate

	local function OpenLid()
		if lid then
			local tweenService = game:GetService("TweenService")
			local tweenInfo = TweenInfo.new(1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
			local properties = {CFrame = lid.CFrame * CFrame.Angles(0, math.rad(90), 0)}
			local tween = tweenService:Create(lid, tweenInfo, properties)
			tween:Play()
		end

		print("Ammo Crate Opened!")
	end

	prompt.Triggered:Connect(function()
		OpenLid()
		prompt:Destroy()
	end)
end)

if not success then
	warn("[AmmoCrateInteraction] Failed to set up crate prompt: " .. tostring(err))
end
