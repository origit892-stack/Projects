local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Tokens = require(ReplicatedStorage.UI.Tokens)

local StatChip = {
    create = function(props)
        local chip = Instance.new("Frame")
        chip.Name = props.Name or "StatChip"
        chip.Size = props.Size or UDim2.new(0, 100, 0, 30)
        chip.Position = props.Position or UDim2.new(0.5, -50, 0.5, -15)
        chip.AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0.5)
        chip.LayoutOrder = props.LayoutOrder or 0
        chip.BackgroundTransparency = 1
        chip.BorderSizePixel = 0
        chip.Parent = props.Parent or game.Players.LocalPlayer:WaitForChild("PlayerGui")
        
        local label = Instance.new("TextLabel")
        label.Name = "Label"
        label.Parent = chip
        label.Text = props.Label or ""
        label.TextSize = Tokens.TextSize.Caption
        label.TextColor3 = Tokens.Color.TextSecondary
        label.BackgroundTransparency = 1
        label.Size = UDim2.new(0.62, -12, 1, 0)
        label.Position = UDim2.new(0, 12, 0, 0)
        label.TextXAlignment = Enum.TextXAlignment.Left
        
        local value = Instance.new("TextLabel")
        value.Name = "Value"
        value.Parent = chip
        value.Text = props.Value or ""
        value.TextSize = Tokens.TextSize.Body
        value.TextColor3 = Tokens.Color.TextPrimary
        value.BackgroundTransparency = 1
        value.Size = UDim2.new(0.38, -12, 1, 0)
        value.Position = UDim2.new(0.62, 0, 0, 0)
        value.TextXAlignment = Enum.TextXAlignment.Right
        
        return chip
    end,
    
    setValue = function(self, value)
        self.Value.Text = value
    end,
    
    setLabel = function(self, label)
        self.Label.Text = label
    end,
    
    destroy = function(self)
        self:Destroy()
    end,
}
return StatChip
