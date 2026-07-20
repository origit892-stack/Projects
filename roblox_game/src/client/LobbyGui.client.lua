--!strict
-- Minimal launcher interaction HUD. The lobby title and station labels are 3D/SurfaceGui.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local screenGui = playerGui:WaitForChild("BunkerGui") :: ScreenGui
local remote = ReplicatedStorage:WaitForChild("RemoteEvents"):WaitForChild("GroupTeleportEvent") :: RemoteEvent

local panel = Instance.new("Frame")
panel.Name = "LauncherPrompt"
panel.AnchorPoint = Vector2.new(0.5, 1)
panel.Position = UDim2.fromScale(0.5, 1.08)
panel.Size = UDim2.fromOffset(440, 150)
panel.BackgroundColor3 = Color3.fromRGB(10, 13, 12)
panel.BackgroundTransparency = 0.08
panel.BorderSizePixel = 0
panel.Visible = false
panel.Parent = screenGui

local sizeConstraint = Instance.new("UISizeConstraint")
sizeConstraint.MinSize = Vector2.new(300, 130)
sizeConstraint.MaxSize = Vector2.new(520, 170)
sizeConstraint.Parent = panel

local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(55, 220, 95)
stroke.Thickness = 2
stroke.Transparency = 0.25
stroke.Parent = panel

local title = Instance.new("TextLabel")
title.Name = "Station"
title.Position = UDim2.fromOffset(18, 12)
title.Size = UDim2.new(1, -36, 0, 32)
title.BackgroundTransparency = 1
title.Font = Enum.Font.Code
title.Text = "START GAME"
title.TextColor3 = Color3.fromRGB(80, 240, 110)
title.TextSize = 25
title.TextXAlignment = Enum.TextXAlignment.Left
title.Parent = panel

local detail = Instance.new("TextLabel")
detail.Name = "Detail"
detail.Position = UDim2.fromOffset(18, 47)
detail.Size = UDim2.new(1, -36, 0, 24)
detail.BackgroundTransparency = 1
detail.Font = Enum.Font.Code
detail.Text = "1 PLAYER DETECTED"
detail.TextColor3 = Color3.fromRGB(170, 178, 168)
detail.TextSize = 16
detail.TextXAlignment = Enum.TextXAlignment.Left
detail.Parent = panel

local launch = Instance.new("TextButton")
launch.Name = "Launch"
launch.AnchorPoint = Vector2.new(1, 1)
launch.Position = UDim2.new(1, -16, 1, -14)
launch.Size = UDim2.fromOffset(180, 46)
launch.BackgroundColor3 = Color3.fromRGB(116, 24, 20)
launch.AutoButtonColor = true
launch.Font = Enum.Font.GothamBold
launch.Text = "LAUNCH  [E]"
launch.TextColor3 = Color3.fromRGB(245, 238, 225)
launch.TextSize = 17
launch.Parent = panel

local hint = Instance.new("TextLabel")
hint.Position = UDim2.fromOffset(18, 96)
hint.Size = UDim2.new(1, -230, 0, 30)
hint.BackgroundTransparency = 1
hint.Font = Enum.Font.Gotham
hint.Text = "Destination: BunkerGame"
hint.TextColor3 = Color3.fromRGB(132, 138, 130)
hint.TextSize = 14
hint.TextXAlignment = Enum.TextXAlignment.Left
hint.Parent = panel

local hideToken = 0
local function showPanel(label: string, groupSize: number)
	hideToken += 1
	local token = hideToken
	panel.Visible = true
	title.Text = tostring(label):upper()
	detail.Text = string.format("%d PLAYER%s DETECTED", groupSize, if groupSize == 1 then "" else "S")
	TweenService:Create(panel, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Position = UDim2.new(0.5, 0, 1, -28),
	}):Play()
	task.delay(2.5, function()
		if token ~= hideToken then return end
		TweenService:Create(panel, TweenInfo.new(0.18), { Position = UDim2.fromScale(0.5, 1.08) }):Play()
		task.delay(0.2, function()
			if token == hideToken then panel.Visible = false end
		end)
	end)
end

launch.Activated:Connect(function()
	launch.Text = "LAUNCHING..."
	remote:FireServer("TeleportNow")
end)

remote.OnClientEvent:Connect(function(action: string, data: any)
	if action == "PadNearby" then
		showPanel(data.label or "START GAME", data.groupSize or 1)
	elseif action == "Teleporting" then
		panel.Visible = true
		detail.Text = string.format("TRANSFERRING %d PLAYER(S)...", data)
		launch.Text = "PLEASE WAIT"
	elseif action == "StudioPreview" then
		detail.Text = "STUDIO TEST PASSED — TARGET " .. tostring(data)
		launch.Text = "LAUNCH  [E]"
	elseif action == "Rejected" then
		detail.Text = tostring(data):upper()
		detail.TextColor3 = Color3.fromRGB(235, 90, 70)
		launch.Text = "TRY AGAIN"
	end
end)
