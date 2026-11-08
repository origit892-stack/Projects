local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Tokens = require(ReplicatedStorage.UI.Tokens)

local ProgressBar = {
    create = function(props)
        local bar = Instance.new("Frame")
        bar.Name = props.Name or "ProgressBar"
        bar.Size = props.Size or UDim2.new(0, 200, 0, 20)
        bar.Position = props.Position or UDim2.new(0.5, -100, 0.5, -10)
        bar.AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0.5)
        bar.LayoutOrder = props.LayoutOrder or 0
        bar.BackgroundColor3 = Tokens.Color.SurfaceRaised
        bar.BackgroundTransparency = Tokens.Transparency.Surface
        bar.BorderSizePixel = 0
        bar.Visible = props.Visible == true
        bar.Parent = props.Parent or game.Players.LocalPlayer:WaitForChild("PlayerGui")
        
        local fill = Instance.new("Frame")
        fill.Name = "Fill"
        fill.Parent = bar
        fill.Size = UDim2.new(0, 0, 1, 0)
        fill.Position = UDim2.new(0, 0, 0, 0)
        fill.BackgroundColor3 = Tokens.Color.Accent
        
        local label = Instance.new("TextLabel")
        label.Name = "Label"
        label.Parent = bar
        label.Text = props.Label or ""
        label.TextSize = Tokens.TextSize.Body
        label.TextColor3 = Tokens.Color.TextPrimary
        label.BackgroundTransparency = 1
        label.Size = UDim2.new(1, 0, 1, 0)
        label.Position = UDim2.new(0, 0, 0, 0)
        
        return bar
    end,
    
    setProgress = function(self, progress)
        local normalized = math.clamp(progress, 0, 1)
        self.Fill.Size = UDim2.new(normalized, 0, 1, 0)
        self.Visible = normalized > 0
    end,
    
    setLabel = function(self, label)
        self.Label.Text = label
    end,
    
    setVisible = function(self, visible)
        self.Visible = visible
    end,
    
    destroy = function(self)
        self:Destroy()
    end,
}
return ProgressBar
