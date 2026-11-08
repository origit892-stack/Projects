local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Tokens = require(ReplicatedStorage.UI.Tokens)

local Notification = {
    create = function(props)
        local notification = Instance.new("Frame")
        notification.Name = props.Name or "Notification"
        notification.Size = props.Size or UDim2.new(0, 300, 0, 60)
        notification.Position = props.Position or UDim2.new(0.5, -150, 0.1, 0)
        notification.AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0)
        notification.LayoutOrder = props.LayoutOrder or 0
        notification.BackgroundColor3 = Tokens.Color.SurfaceRaised
        notification.BackgroundTransparency = Tokens.Transparency.Surface
        notification.BorderSizePixel = 0
        notification.Parent = props.Parent or game.Players.LocalPlayer:WaitForChild("PlayerGui")
        
        local background = Instance.new("Frame")
        background.Name = "Background"
        background.Parent = notification
        background.Size = UDim2.new(1, 0, 1, 0)
        background.Position = UDim2.new(0, 0, 0, 0)
        background.BackgroundColor3 = Tokens.Color.Machine
        background.BackgroundTransparency = 0
        background.BorderSizePixel = 0
        background.Size = UDim2.new(0, 4, 1, 0)
        
        local text = Instance.new("TextLabel")
        text.Name = "Text"
        text.Parent = notification
        text.Text = props.Text or ""
        text.TextSize = Tokens.TextSize.Body
        text.TextColor3 = Tokens.Color.TextPrimary
        text.BackgroundTransparency = 1
        text.Size = UDim2.new(1, -28, 1, 0)
        text.Position = UDim2.new(0, 18, 0, 0)
        text.TextXAlignment = Enum.TextXAlignment.Left
        
        return notification
    end,
    
    show = function(self, text, variant)
        self.Text.Text = text
        
        if variant == "Info" then
            self.Background.BackgroundColor3 = Tokens.Color.Machine
        elseif variant == "Success" then
            self.Background.BackgroundColor3 = Tokens.Color.Success
        elseif variant == "Warning" then
            self.Background.BackgroundColor3 = Tokens.Color.Warning
        elseif variant == "Danger" then
            self.Background.BackgroundColor3 = Tokens.Color.Danger
        end
    end,
    
    destroy = function(self)
        self:Destroy()
    end,
}
return Notification
