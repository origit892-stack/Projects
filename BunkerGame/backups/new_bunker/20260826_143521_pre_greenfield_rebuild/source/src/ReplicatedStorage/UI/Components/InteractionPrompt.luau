--!strict

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local Tokens = require(ReplicatedStorage.UI.Tokens)

export type PromptView = {
    Gui: ScreenGui,
    Root: CanvasGroup,
    Scale: UIScale,
    InputButton: TextButton,
    InputImage: ImageLabel,
    InputLabel: TextLabel,
    HoldLabel: TextLabel,
    ActionLabel: TextLabel,
    ObjectLabel: TextLabel,
    ProgressTrack: Frame,
    ProgressFill: Frame,
    AccentRail: Frame,
    setContent: (self: PromptView, inputText: string, inputImage: string?, actionText: string, objectText: string, isHold: boolean) -> (),
    setProgress: (self: PromptView, progress: number) -> (),
    setViewportScale: (self: PromptView, scale: number) -> (),
    show: (self: PromptView) -> (),
    hide: (self: PromptView, immediate: boolean?) -> (),
    showFeedback: (self: PromptView, tone: string) -> (),
    destroy: (self: PromptView) -> (),
}

local ENTER_TWEEN = TweenInfo.new(Tokens.Motion.Normal, Enum.EasingStyle.Quart, Enum.EasingDirection.Out)
local EXIT_TWEEN = TweenInfo.new(Tokens.Motion.Fast, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
local FEEDBACK_TWEEN = TweenInfo.new(Tokens.Motion.Fast, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)

local InteractionPrompt = {}
local PromptViewMethods = {}
PromptViewMethods.__index = PromptViewMethods

local function corner(parent: Instance, radius: number)
    local uiCorner = Instance.new("UICorner")
    uiCorner.CornerRadius = UDim.new(0, radius)
    uiCorner.Parent = parent
end

local function stroke(parent: Instance, color: Color3, thickness: number, transparency: number?)
    local uiStroke = Instance.new("UIStroke")
    uiStroke.Color = color
    uiStroke.Thickness = thickness
    uiStroke.Transparency = transparency or 0
    uiStroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
    uiStroke.Parent = parent
end

local function textLabel(name: string, parent: Instance, size: UDim2, position: UDim2): TextLabel
    local label = Instance.new("TextLabel")
    label.Name = name
    label.BackgroundTransparency = 1
    label.Size = size
    label.Position = position
    label.Font = Enum.Font.GothamMedium
    label.TextColor3 = Tokens.Color.TextPrimary
    label.TextStrokeColor3 = Tokens.Color.Overlay
    label.TextStrokeTransparency = 0.72
    label.TextXAlignment = Enum.TextXAlignment.Left
    label.TextYAlignment = Enum.TextYAlignment.Center
    label.TextTruncate = Enum.TextTruncate.AtEnd
    label.Parent = parent
    return label
end

function InteractionPrompt.create(parent: PlayerGui): PromptView
    local gui = Instance.new("ScreenGui")
    gui.Name = "BunkerInteractionUI"
    gui.DisplayOrder = Tokens.Layer.Modal
    gui.IgnoreGuiInset = false
    gui.ResetOnSpawn = false
    gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    gui.Parent = parent

    local root = Instance.new("CanvasGroup")
    root.Name = "Prompt"
    root.AnchorPoint = Vector2.new(0.5, 1)
    root.Position = UDim2.fromScale(0.5, 0.84)
    root.Size = UDim2.new(0.9, 0, 0, Tokens.Layout.PromptHeight)
    root.BackgroundColor3 = Tokens.Interaction.Surface
    root.BackgroundTransparency = Tokens.Transparency.Surface
    root.BorderSizePixel = 0
    root.GroupTransparency = 1
    root.Visible = false
    root.Parent = gui
    corner(root, Tokens.Radius.SM)
    stroke(root, Tokens.Interaction.SurfaceEdge, Tokens.Stroke.Thin)

    local sizeConstraint = Instance.new("UISizeConstraint")
    sizeConstraint.MinSize = Vector2.new(300, Tokens.Layout.PromptHeight)
    sizeConstraint.MaxSize = Vector2.new(Tokens.Layout.PromptWidth, Tokens.Layout.PromptHeight)
    sizeConstraint.Parent = root

    local scale = Instance.new("UIScale")
    scale.Name = "ResponsiveScale"
    scale.Scale = 0.96
    scale.Parent = root

    local shadow = Instance.new("Frame")
    shadow.Name = "Shadow"
    shadow.AnchorPoint = Vector2.new(0.5, 0.5)
    shadow.Position = UDim2.new(0.5, 0, 0.5, 4)
    shadow.Size = UDim2.new(1, 8, 1, 8)
    shadow.BackgroundColor3 = Tokens.Color.Overlay
    shadow.BackgroundTransparency = 0.58
    shadow.BorderSizePixel = 0
    shadow.ZIndex = 0
    shadow.Parent = root
    corner(shadow, Tokens.Radius.SM)

    local accentRail = Instance.new("Frame")
    accentRail.Name = "StatusRail"
    accentRail.Position = UDim2.fromOffset(0, 0)
    accentRail.Size = UDim2.new(0, 4, 1, 0)
    accentRail.BackgroundColor3 = Tokens.Interaction.Rail
    accentRail.BorderSizePixel = 0
    accentRail.ZIndex = 2
    accentRail.Parent = root

    local inputButton = Instance.new("TextButton")
    inputButton.Name = "InputGlyph"
    inputButton.AnchorPoint = Vector2.new(0, 0.5)
    inputButton.Position = UDim2.new(0, 17, 0.5, 0)
    inputButton.Size = UDim2.fromOffset(58, 58)
    inputButton.BackgroundColor3 = Tokens.Interaction.KeySurface
    inputButton.BorderSizePixel = 0
    inputButton.AutoButtonColor = false
    inputButton.Text = ""
    inputButton.ZIndex = 3
    inputButton.Parent = root
    corner(inputButton, Tokens.Radius.SM)
    stroke(inputButton, Tokens.Interaction.KeyEdge, Tokens.Stroke.Thin)

    local inputImage = Instance.new("ImageLabel")
    inputImage.Name = "GamepadGlyph"
    inputImage.AnchorPoint = Vector2.new(0.5, 0.5)
    inputImage.Position = UDim2.fromScale(0.5, 0.5)
    inputImage.Size = UDim2.fromOffset(34, 34)
    inputImage.BackgroundTransparency = 1
    inputImage.ImageColor3 = Tokens.Color.TextPrimary
    inputImage.ScaleType = Enum.ScaleType.Fit
    inputImage.Visible = false
    inputImage.ZIndex = 4
    inputImage.Parent = inputButton

    local inputLabel = textLabel("Key", inputButton, UDim2.fromScale(1, 1), UDim2.fromScale(0, 0))
    inputLabel.Font = Enum.Font.GothamBold
    inputLabel.Text = "E"
    inputLabel.TextSize = Tokens.TextSize.Heading
    inputLabel.TextXAlignment = Enum.TextXAlignment.Center
    inputLabel.ZIndex = 4

    local holdLabel = textLabel("Hold", inputButton, UDim2.new(1, 0, 0, 14), UDim2.new(0, 0, 1, -16))
    holdLabel.Font = Enum.Font.GothamBold
    holdLabel.Text = "HOLD"
    holdLabel.TextColor3 = Tokens.Color.TextMuted
    holdLabel.TextSize = Tokens.TextSize.Caption
    holdLabel.TextXAlignment = Enum.TextXAlignment.Center
    holdLabel.Visible = false
    holdLabel.ZIndex = 5

    local actionLabel = textLabel("Action", root, UDim2.new(1, -104, 0, 28), UDim2.fromOffset(92, 15))
    actionLabel.Font = Enum.Font.GothamBold
    actionLabel.Text = "INTERACT"
    actionLabel.TextColor3 = Tokens.Color.TextPrimary
    actionLabel.TextSize = Tokens.TextSize.Label
    actionLabel.ZIndex = 3

    local objectLabel = textLabel("Object", root, UDim2.new(1, -104, 0, 22), UDim2.fromOffset(92, 43))
    objectLabel.Font = Enum.Font.GothamMedium
    objectLabel.Text = "BUNKER SYSTEM"
    objectLabel.TextColor3 = Tokens.Color.TextSecondary
    objectLabel.TextSize = Tokens.TextSize.Caption
    objectLabel.ZIndex = 3

    local divider = Instance.new("Frame")
    divider.Name = "Divider"
    divider.Position = UDim2.fromOffset(91, 66)
    divider.Size = UDim2.new(1, -108, 0, 1)
    divider.BackgroundColor3 = Tokens.Color.Stroke
    divider.BackgroundTransparency = 0.35
    divider.BorderSizePixel = 0
    divider.ZIndex = 2
    divider.Parent = root

    local progressTrack = Instance.new("Frame")
    progressTrack.Name = "HoldProgress"
    progressTrack.Position = UDim2.fromOffset(92, 72)
    progressTrack.Size = UDim2.new(1, -110, 0, 3)
    progressTrack.BackgroundColor3 = Tokens.Color.Stroke
    progressTrack.BackgroundTransparency = 0.25
    progressTrack.BorderSizePixel = 0
    progressTrack.Visible = false
    progressTrack.ZIndex = 3
    progressTrack.Parent = root

    local progressFill = Instance.new("Frame")
    progressFill.Name = "Fill"
    progressFill.Size = UDim2.fromScale(0, 1)
    progressFill.BackgroundColor3 = Tokens.Interaction.Progress
    progressFill.BorderSizePixel = 0
    progressFill.ZIndex = 4
    progressFill.Parent = progressTrack

    local view = setmetatable({
        Gui = gui,
        Root = root,
        Scale = scale,
        InputButton = inputButton,
        InputImage = inputImage,
        InputLabel = inputLabel,
        HoldLabel = holdLabel,
        ActionLabel = actionLabel,
        ObjectLabel = objectLabel,
        ProgressTrack = progressTrack,
        ProgressFill = progressFill,
        AccentRail = accentRail,
        _viewportScale = 1,
        _transitionSerial = 0,
        _feedbackSerial = 0,
        _feedbackActive = false,
        _baseActionText = "INTERACT",
    }, PromptViewMethods)

    return (view :: any) :: PromptView
end

function PromptViewMethods:setContent(inputText: string, inputImage: string?, actionText: string, objectText: string, isHold: boolean)
    self.InputLabel.Text = string.upper(inputText)
    self.InputLabel.Visible = inputImage == nil or inputImage == ""
    self.InputImage.Image = inputImage or ""
    self.InputImage.Visible = inputImage ~= nil and inputImage ~= ""
    self._baseActionText = string.upper(if actionText ~= "" then actionText else "INTERACT")
    if not self._feedbackActive then
        self.ActionLabel.Text = self._baseActionText
    end
    self.ObjectLabel.Text = string.upper(if objectText ~= "" then objectText else "BUNKER SYSTEM")
    self.HoldLabel.Visible = isHold
    self.ProgressTrack.Visible = isHold
    self:setProgress(0)
end

function PromptViewMethods:setProgress(progress: number)
    self.ProgressFill.Size = UDim2.fromScale(math.clamp(progress, 0, 1), 1)
end

function PromptViewMethods:setViewportScale(viewportScale: number)
    -- Never shrink the 14px secondary text below its readability floor.
    self._viewportScale = math.clamp(viewportScale, 1, 1.18)
    if self.Root.Visible and self.Root.GroupTransparency < 1 then
        self.Scale.Scale = self._viewportScale
    end
end

function PromptViewMethods:show()
    self._transitionSerial += 1
    self._feedbackSerial += 1
    self._feedbackActive = false
    self.ActionLabel.Text = self._baseActionText
    self.Root.Visible = true
    self.Root.GroupTransparency = 1
    self.Scale.Scale = self._viewportScale * 0.96
    TweenService:Create(self.Root, ENTER_TWEEN, { GroupTransparency = 0 }):Play()
    TweenService:Create(self.Scale, ENTER_TWEEN, { Scale = self._viewportScale }):Play()
end

function PromptViewMethods:hide(immediate: boolean?)
    self._transitionSerial += 1
    self._feedbackSerial += 1
    self._feedbackActive = false
    local serial = self._transitionSerial
    if immediate then
        self.Root.GroupTransparency = 1
        self.Root.Visible = false
        self:setProgress(0)
        return
    end

    TweenService:Create(self.Root, EXIT_TWEEN, { GroupTransparency = 1 }):Play()
    TweenService:Create(self.Scale, EXIT_TWEEN, { Scale = self._viewportScale * 0.98 }):Play()
    task.delay(Tokens.Motion.Fast, function()
        if self._transitionSerial == serial then
            self.Root.Visible = false
            self:setProgress(0)
        end
    end)
end

function PromptViewMethods:showFeedback(tone: string)
    self._feedbackSerial += 1
    local serial = self._feedbackSerial
    local isUnavailable = tone == "Unavailable"
    local color = if isUnavailable then Tokens.Interaction.Offline else Tokens.Color.Success
    local message = if isUnavailable then "SYSTEM OFFLINE" else "CONFIRMED"
    self._feedbackActive = true
    self.ActionLabel.Text = message
    TweenService:Create(self.AccentRail, FEEDBACK_TWEEN, { BackgroundColor3 = color }):Play()
    TweenService:Create(self.ActionLabel, FEEDBACK_TWEEN, { TextColor3 = color }):Play()

    task.delay(0.42, function()
        if self._feedbackSerial ~= serial or not self.Root.Visible then
            return
        end
        self._feedbackActive = false
        self.ActionLabel.Text = self._baseActionText
        TweenService:Create(self.AccentRail, ENTER_TWEEN, { BackgroundColor3 = Tokens.Interaction.Rail }):Play()
        TweenService:Create(self.ActionLabel, ENTER_TWEEN, { TextColor3 = Tokens.Color.TextPrimary }):Play()
    end)
end

function PromptViewMethods:destroy()
    self.Gui:Destroy()
end

return table.freeze(InteractionPrompt)
