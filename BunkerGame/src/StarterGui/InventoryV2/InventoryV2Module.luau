--!strict
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local InventoryV2Module = {}
InventoryV2Module.__index = InventoryV2Module

local THEME = {
	SkyBlue = Color3.fromHex("4A90D9"),
	GrassGreen = Color3.fromHex("5CB85C"),
	SunnyYellow = Color3.fromHex("F0C040"),
	CloudWhite = Color3.fromHex("FFFFFF"),
	PanelCream = Color3.fromHex("FFF6DE"),
	HoverGlow = Color3.fromHex("FFF1B8"),
	OutlineDark = Color3.fromHex("2C3E50"),
	TextWhite = Color3.fromHex("FFFFFF"),
	TextDark = Color3.fromHex("2C3E50"),
	ChargeHigh = Color3.fromHex("5CB85C"),
	ChargeMed = Color3.fromHex("F0C040"),
	ChargeLow = Color3.fromHex("E74C3C"),
}

local FONT = Enum.Font.FredokaOne

local function applyVerticalGradient(target: GuiObject, factor: number)
	local grad = Instance.new("UIGradient")
	grad.Rotation = 90
	grad.Color = ColorSequence.new({
		ColorSequenceKeypoint.new(0, Color3.new(1, 1, 1)),
		ColorSequenceKeypoint.new(1, Color3.new(1 - factor, 1 - factor, 1 - factor))
	})
	grad.Parent = target
	return grad
end

local function applyCorner(target: GuiObject, px: number)
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, px)
	corner.Parent = target
	return corner
end

local function applyStroke(target: GuiObject, color: Color3, transp: number, thickness: number?)
	local stroke = Instance.new("UIStroke")
	stroke.Color = color
	stroke.Transparency = transp
	stroke.Thickness = thickness or 3
	stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	stroke.Parent = target
	return stroke
end

-- Builds a simple red cube preview inside a ViewportFrame with a dedicated
-- Camera aimed directly at the cube. A rotation loop spins the cube around
-- its Y axis. Returns a teardown function that disconnects the loop and
-- destroys all 3D content (cube, camera) to prevent memory leaks.
local function createItemPreview(viewport: ViewportFrame)
	viewport.BackgroundTransparency = 1

	local cube = Instance.new("Part")
	cube.Name = "PreviewCube"
	cube.Size = Vector3.new(2, 2, 2)
	cube.Color = Color3.new(1, 0, 0)
	cube.Anchored = true
	cube.CanCollide = false
	cube.CFrame = CFrame.new(0, 0, 0)
	cube.Parent = viewport

	-- ViewportFrame ignores light instances; use full-bright ambient lighting
	-- so the cube is clearly visible.
	viewport.Ambient = Color3.new(1, 1, 1)
	viewport.LightColor = Color3.new(1, 1, 1)

	local camera = Instance.new("Camera")
	camera.FieldOfView = 32
	camera.BackgroundTransparency = 1
	camera.CFrame = CFrame.lookAt(Vector3.new(0, 0, 6), Vector3.new(0, 0, 0))
	camera.Parent = viewport
	viewport.CurrentCamera = camera

	local connection = RunService.RenderStepped:Connect(function()
		cube.CFrame = CFrame.new(0, 0, 0) * CFrame.Angles(0, os.clock(), 0)
	end)

	return function()
		connection:Disconnect()
		if cube.Parent ~= nil then
			cube:Destroy()
		end
		if camera.Parent ~= nil then
			camera:Destroy()
		end
	end
end

function InventoryV2Module.new()
	local self = setmetatable({}, InventoryV2Module)
	self._mounted = false
	self._selectedSlot = nil
	self._connections = {} :: { RBXScriptConnection }
	return self
end

function InventoryV2Module:Init()
	return true
end

function InventoryV2Module:Mount(parent: ScreenGui)
	if self._mounted then return end

	local rootCanvas = Instance.new("CanvasGroup")
	rootCanvas.Name = "InventoryV2_Root"
	rootCanvas.Size = UDim2.new(0, 920, 0, 610)
	rootCanvas.Position = UDim2.new(0.5, -460, 0.5, -305)
	rootCanvas.BackgroundColor3 = THEME.SkyBlue
	rootCanvas.BackgroundTransparency = 0
	rootCanvas.BorderSizePixel = 0
	applyCorner(rootCanvas, 12)
	applyStroke(rootCanvas, THEME.OutlineDark, 0, 4)
	applyVerticalGradient(rootCanvas, 0.08)
	rootCanvas.Parent = parent

	-- Classic Roblox stud texture overlay (tiled, subtle) behind all content
	local studTexture = Instance.new("ImageLabel")
	studTexture.Name = "StudTexture"
	studTexture.Size = UDim2.fromScale(1, 1)
	studTexture.Image = "rbxassetid://7447638611"
	studTexture.ScaleType = Enum.ScaleType.Tile
	studTexture.TileSize = UDim2.new(0, 32, 0, 32)
	studTexture.ZIndex = 0
	studTexture.ImageTransparency = 0.5
	studTexture.BackgroundTransparency = 1
	studTexture.BorderSizePixel = 0
	studTexture.Parent = rootCanvas

	-- Top Header Bar
	local header = Instance.new("Frame")
	header.Name = "Header"
	header.Size = UDim2.new(1, 0, 0, 48)
	header.BackgroundColor3 = THEME.GrassGreen
	header.BackgroundTransparency = 0
	header.BorderSizePixel = 0
	applyStroke(header, THEME.OutlineDark, 0, 3)
	header.Parent = rootCanvas

	local titleLabel = Instance.new("TextLabel")
	titleLabel.Size = UDim2.new(0, 300, 1, 0)
	titleLabel.Position = UDim2.new(0, 20, 0, 0)
	titleLabel.BackgroundTransparency = 1
	titleLabel.Font = FONT
	titleLabel.TextSize = 20
	titleLabel.TextColor3 = THEME.TextWhite
	titleLabel.Text = "MY INVENTORY"
	titleLabel.TextXAlignment = Enum.TextXAlignment.Left
	titleLabel.TextStroke = true
	titleLabel.TextStrokeColor = THEME.OutlineDark
	titleLabel.TextStrokeTransparency = 0
	titleLabel.Parent = header

	-- Close ("X") Button
	local closeButton = Instance.new("TextButton")
	closeButton.Name = "CloseButton"
	closeButton.Size = UDim2.new(0, 32, 0, 32)
	closeButton.Position = UDim2.new(1, -40, 0.5, 0)
	closeButton.AnchorPoint = Vector2.new(0, 0.5)
	closeButton.BackgroundColor3 = THEME.SunnyYellow
	closeButton.TextColor3 = THEME.TextDark
	closeButton.Font = FONT
	closeButton.TextSize = 14
	closeButton.Text = "X"
	closeButton.AutoButtonColor = false
	applyCorner(closeButton, 8)
	local closeStroke = applyStroke(closeButton, THEME.OutlineDark, 0, 3)
	closeButton.Parent = header

	closeButton.MouseEnter:Connect(function()
		TweenService:Create(closeButton, TweenInfo.new(0.15), {BackgroundColor3 = THEME.GrassGreen}):Play()
		TweenService:Create(closeStroke, TweenInfo.new(0.15), {Color = THEME.GrassGreen, Transparency = 0}):Play()
	end)
	closeButton.MouseLeave:Connect(function()
		TweenService:Create(closeButton, TweenInfo.new(0.15), {BackgroundColor3 = THEME.SunnyYellow}):Play()
		TweenService:Create(closeStroke, TweenInfo.new(0.15), {Color = THEME.OutlineDark, Transparency = 0}):Play()
	end)
	closeButton.Activated:Connect(function()
		rootCanvas.Visible = false
	end)

	-- Left Container (60%)
	local leftFrame = Instance.new("Frame")
	leftFrame.Name = "LeftContainer"
	leftFrame.Size = UDim2.new(0.58, 0, 0, 540)
	leftFrame.Position = UDim2.new(0, 16, 0, 56)
	leftFrame.BackgroundColor3 = THEME.PanelCream
	leftFrame.BackgroundTransparency = 0
	applyCorner(leftFrame, 10)
	applyStroke(leftFrame, THEME.OutlineDark, 0, 3)
	leftFrame.Parent = rootCanvas

	-- Category Tabs Row
	local tabRow = Instance.new("Frame")
	tabRow.Name = "TabRow"
	tabRow.Size = UDim2.new(1, -16, 0, 36)
	tabRow.Position = UDim2.new(0, 8, 0, 8)
	tabRow.BackgroundTransparency = 1
	tabRow.Parent = leftFrame

	local tabLayout = Instance.new("UIListLayout")
	tabLayout.FillDirection = Enum.FillDirection.Horizontal
	tabLayout.Padding = UDim.new(0, 6)
	tabLayout.Parent = tabRow

	local categories = {"WEAPONS", "TOOLS", "FOOD", "PETS", "MISC"}
	for i, catName in ipairs(categories) do
		local tabBtn = Instance.new("TextButton")
		tabBtn.Name = "Tab_" .. catName
		tabBtn.Size = UDim2.new(0.19, 0, 1, 0)
		tabBtn.BackgroundColor3 = (i == 1) and THEME.GrassGreen or THEME.CloudWhite
		tabBtn.TextColor3 = (i == 1) and THEME.TextWhite or THEME.TextDark
		tabBtn.Font = FONT
		tabBtn.TextSize = 11
		tabBtn.Text = catName
		applyCorner(tabBtn, 8)
		applyStroke(tabBtn, THEME.OutlineDark, 0, 3)

		if i == 1 then
			local glowIndicator = Instance.new("Frame")
			glowIndicator.Size = UDim2.new(1, 0, 0, 3)
			glowIndicator.Position = UDim2.new(0, 0, 1, -3)
			glowIndicator.BackgroundColor3 = THEME.SunnyYellow
			glowIndicator.BorderSizePixel = 0
			glowIndicator.Parent = tabBtn
		end

		tabBtn.Parent = tabRow
	end

	-- 5x4 Grid
	local gridFrame = Instance.new("ScrollingFrame")
	gridFrame.Name = "SlotGrid"
	gridFrame.Size = UDim2.new(1, -16, 1, -60)
	gridFrame.Position = UDim2.new(0, 8, 0, 52)
	gridFrame.BackgroundTransparency = 1
	gridFrame.ScrollBarThickness = 4
	gridFrame.ScrollBarImageColor3 = THEME.GrassGreen
	gridFrame.Parent = leftFrame

	local uigrid = Instance.new("UIGridLayout")
	uigrid.CellSize = UDim2.new(0, 98, 0, 98)
	uigrid.CellPadding = UDim2.new(0, 7, 0, 7)
	uigrid.Parent = gridFrame

	for s = 1, 20 do
		local slot = Instance.new("Frame")
		slot.Name = "Slot_" .. s
		slot.BackgroundColor3 = THEME.CloudWhite
		slot.BackgroundTransparency = 0
		applyCorner(slot, 8)
		local slotStroke = applyStroke(slot, THEME.OutlineDark, 0, 3)
		applyVerticalGradient(slot, 0.08)

		-- Inner recessed layer
		local inset = Instance.new("Frame")
		inset.Size = UDim2.new(1, -6, 1, -6)
		inset.Position = UDim2.new(0, 3, 0, 3)
		inset.BackgroundColor3 = THEME.PanelCream
		inset.BackgroundTransparency = 0.4
		applyCorner(inset, 5)
		inset.Parent = slot

		-- Stack Badge
		local badge = Instance.new("TextLabel")
		badge.Size = UDim2.new(0, 28, 0, 14)
		badge.Position = UDim2.new(1, -30, 1, -16)
		badge.BackgroundColor3 = THEME.SunnyYellow
		badge.TextColor3 = THEME.TextDark
		badge.Font = FONT
		badge.TextSize = 10
		badge.Text = "x" .. tostring(s % 5 + 1)
		applyCorner(badge, 4)
		applyStroke(badge, THEME.OutlineDark, 0, 2)
		badge.Parent = slot

		-- 2px Charge Bar
		local chargeBg = Instance.new("Frame")
		chargeBg.Size = UDim2.new(1, -8, 0, 2)
		chargeBg.Position = UDim2.new(0, 4, 1, -4)
		chargeBg.BackgroundColor3 = THEME.OutlineDark
		chargeBg.BorderSizePixel = 0
		chargeBg.Parent = slot

		local chargeFill = Instance.new("Frame")
		local pct = math.clamp(1 - (s * 0.04), 0.2, 1)
		chargeFill.Size = UDim2.new(pct, 0, 1, 0)
		chargeFill.BackgroundColor3 = (pct > 0.6) and THEME.ChargeHigh or ((pct > 0.35) and THEME.ChargeMed or THEME.ChargeLow)
		chargeFill.BorderSizePixel = 0
		chargeFill.Parent = chargeBg

		-- Bright hover pop
		slot.MouseEnter:Connect(function()
			TweenService:Create(slotStroke, TweenInfo.new(0.2), {Color = THEME.SunnyYellow, Transparency = 0}):Play()
			TweenService:Create(slot, TweenInfo.new(0.2), {BackgroundColor3 = THEME.HoverGlow}):Play()
		end)
		slot.MouseLeave:Connect(function()
			TweenService:Create(slotStroke, TweenInfo.new(0.2), {Color = THEME.OutlineDark, Transparency = 0}):Play()
			TweenService:Create(slot, TweenInfo.new(0.2), {BackgroundColor3 = THEME.CloudWhite}):Play()
		end)

		slot.Parent = gridFrame
	end

	-- Right Inspect Panel (40%)
	local rightFrame = Instance.new("Frame")
	rightFrame.Name = "InspectPanel"
	rightFrame.Size = UDim2.new(0.38, 0, 0, 540)
	rightFrame.Position = UDim2.new(0.605, 0, 0, 56)
	rightFrame.BackgroundColor3 = THEME.PanelCream
	rightFrame.BackgroundTransparency = 0
	applyCorner(rightFrame, 10)
	applyStroke(rightFrame, THEME.OutlineDark, 0, 3)
	rightFrame.Parent = rootCanvas

	-- Item Classification Header
	local inspectClass = Instance.new("TextLabel")
	inspectClass.Size = UDim2.new(1, -24, 0, 18)
	inspectClass.Position = UDim2.new(0, 12, 0, 12)
	inspectClass.BackgroundTransparency = 1
	inspectClass.Font = FONT
	inspectClass.TextSize = 11
	inspectClass.TextColor3 = THEME.GrassGreen
	inspectClass.Text = "LEGENDARY SUPER TOY"
	inspectClass.TextXAlignment = Enum.TextXAlignment.Left
	inspectClass.Parent = rightFrame

	local inspectName = Instance.new("TextLabel")
	inspectName.Size = UDim2.new(1, -24, 0, 24)
	inspectName.Position = UDim2.new(0, 12, 0, 30)
	inspectName.BackgroundTransparency = 1
	inspectName.Font = FONT
	inspectName.TextSize = 18
	inspectName.TextColor3 = THEME.TextDark
	inspectName.Text = "MEGA BLASTER 3000"
	inspectName.TextXAlignment = Enum.TextXAlignment.Left
	inspectName.Parent = rightFrame

	-- Item Model Viewport Preview Box
	local modelBox = Instance.new("Frame")
	modelBox.Size = UDim2.new(1, -24, 0, 150)
	modelBox.Position = UDim2.new(0, 12, 0, 62)
	modelBox.BackgroundColor3 = THEME.CloudWhite
	modelBox.BackgroundTransparency = 0
	applyCorner(modelBox, 10)
	applyStroke(modelBox, THEME.OutlineDark, 0, 3)
	modelBox.Parent = rightFrame

	local modelViewport = Instance.new("ViewportFrame")
	modelViewport.Name = "ItemViewport"
	modelViewport.Size = UDim2.new(1, 0, 1, 0)
	modelViewport.BackgroundTransparency = 1
	modelViewport.BorderSizePixel = 0
	modelViewport.Parent = modelBox

	-- Segmented Stat Bars
	local stats = {
		{Name = "POWER", Segments = 8},
		{Name = "SPEED", Segments = 6},
		{Name = "LUCK", Segments = 7},
		{Name = "FUN", Segments = 9}
	}

	for idx, st in ipairs(stats) do
		local yPos = 226 + ((idx - 1) * 36)
		local stLabel = Instance.new("TextLabel")
		stLabel.Size = UDim2.new(0, 90, 0, 14)
		stLabel.Position = UDim2.new(0, 14, 0, yPos)
		stLabel.BackgroundTransparency = 1
		stLabel.Font = FONT
		stLabel.TextSize = 11
		stLabel.TextColor3 = THEME.TextDark
		stLabel.Text = st.Name
		stLabel.TextXAlignment = Enum.TextXAlignment.Left
		stLabel.Parent = rightFrame

		local barRow = Instance.new("Frame")
		barRow.Size = UDim2.new(0, 200, 0, 10)
		barRow.Position = UDim2.new(0, 110, 0, yPos + 2)
		barRow.BackgroundTransparency = 1
		barRow.Parent = rightFrame

		local blayout = Instance.new("UIListLayout")
		blayout.FillDirection = Enum.FillDirection.Horizontal
		blayout.Padding = UDim.new(0, 3)
		blayout.Parent = barRow

		for seg = 1, 10 do
			local segment = Instance.new("Frame")
			segment.Size = UDim2.new(0, 16, 0, 8)
			segment.BackgroundColor3 = (seg <= st.Segments) and THEME.GrassGreen or THEME.CloudWhite
			segment.BackgroundTransparency = (seg <= st.Segments) and 0 or 0.6
			applyCorner(segment, 2)
			segment.Parent = barRow
		end
	end

	-- Action Buttons
	local btnRow = Instance.new("Frame")
	btnRow.Size = UDim2.new(1, -24, 0, 38)
	btnRow.Position = UDim2.new(0, 12, 1, -50)
	btnRow.BackgroundTransparency = 1
	btnRow.Parent = rightFrame

	local btnLayout = Instance.new("UIListLayout")
	btnLayout.FillDirection = Enum.FillDirection.Horizontal
	btnLayout.Padding = UDim.new(0, 6)
	btnLayout.Parent = btnRow

	local actions = {"EQUIP", "USE", "GIFT"}
	for _, act in ipairs(actions) do
		local btn = Instance.new("TextButton")
		btn.Size = UDim2.new(0.31, 0, 1, 0)
		btn.BackgroundColor3 = (act == "EQUIP") and THEME.GrassGreen or ((act == "USE") and THEME.SunnyYellow or THEME.SkyBlue)
		btn.TextColor3 = (act == "USE") and THEME.TextDark or THEME.TextWhite
		btn.Font = FONT
		btn.TextSize = 13
		btn.Text = act
		applyCorner(btn, 8)
		local bStroke = applyStroke(btn, THEME.OutlineDark, 0, 3)

		btn.MouseEnter:Connect(function()
			TweenService:Create(bStroke, TweenInfo.new(0.15), {Color = THEME.SunnyYellow, Transparency = 0}):Play()
		end)
		btn.MouseLeave:Connect(function()
			TweenService:Create(bStroke, TweenInfo.new(0.15), {Color = THEME.OutlineDark, Transparency = 0}):Play()
		end)

		btn.Parent = btnRow
	end

	-- 3D item preview lifecycle: build the dummy item while the panel is
	-- visible; tear it down (destroy model/camera, disconnect the
	-- rotation loop) when the panel is closed or destroyed. Watching the
	-- Visible property covers both the close button and the B/Tab toggle in
	-- UIController; Destroying covers full GUI teardown.
	local previewTeardown: (() -> ())? = nil
	local function setupPreview()
		if previewTeardown ~= nil then
			return
		end
		previewTeardown = createItemPreview(modelViewport)
	end
	local function teardownPreview()
		if previewTeardown == nil then
			return
		end
		previewTeardown()
		previewTeardown = nil
	end

	table.insert(self._connections, rootCanvas:GetPropertyChangedSignal("Visible"):Connect(function()
		if rootCanvas.Visible then
			setupPreview()
		else
			teardownPreview()
		end
	end))
	table.insert(self._connections, rootCanvas.Destroying:Connect(teardownPreview))

	if rootCanvas.Visible then
		setupPreview()
	end

	self._mounted = true
	return rootCanvas
end

return InventoryV2Module
