--[[
	FarmingUI.client.lua  (StarterGui > FarmingUI)
	Client-side UI: credits display, inventory hotbar, floating notifications,
	and processor progress bar.
--]]

-- ── Services ────────────────────────────────────────────────────────────────
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")
local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

-- ── Remote Events ───────────────────────────────────────────────────────────
local remotes = ReplicatedStorage:WaitForChild("FarmingRemotes")
local UpdateUI      = remotes:WaitForChild("UpdateUI")
local NotifyRE      = remotes:WaitForChild("Notify")
local UpdateProgress = remotes:WaitForChild("UpdateProgress")

-- ── UI Creation ─────────────────────────────────────────────────────────────
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "FarmingUI"
screenGui.IgnoreGuiInset = true
screenGui.ResetOnSpawn = false
screenGui.DisplayOrder = 15
screenGui.Parent = playerGui

-- Helper: create a simple label with common defaults
local function makeLabel(name, text, pos, size, color): TextLabel
	local lbl = Instance.new("TextLabel")
	lbl.Name = name
	lbl.Text = text
	lbl.Position = pos
	lbl.Size = size
	lbl.BackgroundTransparency = 1
	lbl.BorderSizePixel = 0
	lbl.TextColor3 = color or Color3.fromRGB(255, 255, 255)
	lbl.TextScaled = true
	lbl.Font = Enum.Font.GothamBold
	lbl.TextXAlignment = Enum.TextXAlignment.Center
	lbl.Parent = screenGui
	return lbl
end

-- ── Top-Right: Credits ─────────────────────────────────────────────────────
local creditsLabel = makeLabel(
	"CreditsLabel",
	"Credits: 0",
	UDim2.new(1, -200, 0, 10),
	UDim2.new(0, 190, 0, 36),
	Color3.fromRGB(255, 215, 0)   -- gold
)
creditsLabel.TextXAlignment = Enum.TextXAlignment.Right

-- ── Bottom-Centre: Inventory Hotbar ─────────────────────────────────────────
local hotbar = Instance.new("Frame")
hotbar.Name = "Hotbar"
hotbar.Size = UDim2.new(0, 420, 0, 44)
hotbar.Position = UDim2.new(0.5, -210, 1, -60)
hotbar.BackgroundTransparency = 0.4
hotbar.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
hotbar.BorderSizePixel = 0
hotbar.Parent = screenGui

-- UI corner rounding (modern look)
local uic = Instance.new("UICorner", hotbar)
uic.CornerRadius = UDim.new(0, 8)

local seedLbl, cropLbl, foodLbl

do
	local function makeSlot(name, text, xOff)
		local f = Instance.new("Frame")
		f.Name = name
		f.Size = UDim2.new(0, 130, 1, 0)
		f.Position = UDim2.new(0, xOff, 0, 0)
		f.BackgroundTransparency = 1
		f.Parent = hotbar

		local l = Instance.new("TextLabel")
		l.Name = "Count"
		l.Text = text
		l.Size = UDim2.new(1, 0, 1, 0)
		l.BackgroundTransparency = 1
		l.TextColor3 = Color3.fromRGB(255, 255, 255)
		l.TextScaled = true
		l.Font = Enum.Font.GothamBold
		l.Parent = f
		return l
	end

	seedLbl = makeSlot("SeedsSlot",   "[Seeds: 5]",       0)
	cropLbl = makeSlot("CropsSlot",   "[Crops: 0]",       140)
	foodLbl = makeSlot("FoodSlot",    "[Food Items: 0]",  280)
end

-- Colour-coded icons for each slot
seedLbl.TextColor3 = Color3.fromRGB(76, 175, 80)    -- green
cropLbl.TextColor3 = Color3.fromRGB(255, 193, 7)     -- amber
foodLbl.TextColor3 = Color3.fromRGB(33, 150, 243)    -- blue

-- ── Floating Notification System ───────────────────────────────────────────
-- A pool of reusable labels to avoid alloc spam.
local NOTIF_POOL_SIZE = 5
local notifPool: { TextLabel } = {}
local notifIdx = 0

for _ = 1, NOTIF_POOL_SIZE do
	local lbl = makeLabel(
		"Notif",
		"",
		UDim2.new(0.5, -150, 0.4, 0),
		UDim2.new(0, 300, 0, 36),
		Color3.fromRGB(255, 255, 255)
	)
	lbl.TextTransparency = 1
	lbl.Visible = false
	table.insert(notifPool, lbl)
end

local function spawnNotification(text: string)
	notifIdx = notifIdx % NOTIF_POOL_SIZE + 1
	local lbl = notifPool[notifIdx]

	-- Stop any running tween on this label
	local existing = lbl:FindFirstChild("NotifTween")
	if existing then
		existing:Cancel()
		existing:Destroy()
	end

	lbl.Text = text
	lbl.TextTransparency = 0
	lbl.Position = UDim2.new(0.5, -150, 0.4, 0)
	lbl.Visible = true

	-- Float upward + fade out over 1.6 s
	local tween = TweenService:Create(lbl,
		TweenInfo.new(1.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{
			Position         = UDim2.new(0.5, -150, 0.35, 0),
			TextTransparency = 1,
		}
	)
	tween:Play()

	-- Tag so we can cancel it later
	tween.Name = "NotifTween"
	tween.Parent = lbl

	tween.Completed:Connect(function()
		lbl.Visible = false
	end)
end

-- ── Processor Progress Billboard ────────────────────────────────────────────
local progressFill: Frame

-- Processor is created by the server at runtime, so wait for it.
local processorModel = Workspace:WaitForChild("FoodProcessor", 30)
if processorModel then
	local dummy = processorModel:WaitForChild("ProgressDummy", 30)
	if dummy then
		local bb = Instance.new("BillboardGui")
		bb.Name = "ProcessBar"
		bb.Size = UDim2.new(0, 200, 0, 36)
		bb.StudsOffset = Vector3.new(0, 2, 0)
		bb.AlwaysOnTop = true
		bb.Parent = dummy

		local bg = Instance.new("Frame")
		bg.Name = "BG"
		bg.Size = UDim2.new(1, 0, 1, 0)
		bg.BackgroundColor3 = Color3.fromRGB(25, 25, 25)
		bg.BorderSizePixel = 0
		bg.Parent = bb

		local uic2 = Instance.new("UICorner", bg)
		uic2.CornerRadius = UDim.new(0, 6)

		local fill = Instance.new("Frame")
		fill.Name = "Fill"
		fill.Size = UDim2.new(0, 0, 1, 0)
		fill.BackgroundColor3 = Color3.fromRGB(76, 175, 80)
		fill.BorderSizePixel = 0
		fill.Parent = bg

		local uic3 = Instance.new("UICorner", fill)
		uic3.CornerRadius = UDim.new(0, 6)

		local pctLabel = Instance.new("TextLabel")
		pctLabel.Name = "Pct"
		pctLabel.Size = UDim2.new(1, 0, 1, 0)
		pctLabel.BackgroundTransparency = 1
		pctLabel.Text = "0%"
		pctLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
		pctLabel.TextScaled = true
		pctLabel.Font = Enum.Font.GothamBold
		pctLabel.Parent = bb

		progressFill = fill
	end
end

-- ── Remote Event Handlers ───────────────────────────────────────────────────

UpdateUI.OnClientEvent:Connect(function(credits, seeds, crops, food)
	creditsLabel.Text = string.format("Credits: %d", credits)
	seedLbl.Text = string.format("[Seeds: %d]", seeds)
	cropLbl.Text = string.format("[Crops: %d]", crops)
	foodLbl.Text = string.format("[Food Items: %d]", food)
end)

NotifyRE.OnClientEvent:Connect(spawnNotification)

UpdateProgress.OnClientEvent:Connect(function(pct: number)
	if not progressFill then return end
	progressFill.Size = UDim2.new(pct / 100, 0, 1, 0)
	local pctLabel = progressFill.Parent:FindFirstChild("Pct")
	if pctLabel then
		pctLabel.Text = string.format("%.0f%%", pct)
	end
end)

-- ── Periodic cleanup for orphaned tweens (RunService heartbeat) ────────────
RunService.Heartbeat:Connect(function()
	for _, lbl in notifPool do
		if lbl.Visible and lbl.TextTransparency >= 0.99 then
			lbl.Visible = false
		end
	end
end)

print("[FarmingUI] Loaded")
