local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Tokens = require(ReplicatedStorage.UI.Tokens)

local Button = {
    create = function(props)
        local button = Instance.new("TextButton")
        button.Name = props.Name or "Button"
        button.Text = props.Text or ""
        button.Size = props.Size or UDim2.new(0, 100, 0, 30)
        button.Position = props.Position or UDim2.new(0.5, -50, 0.5, -15)
        button.AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0.5)
        button.LayoutOrder = props.LayoutOrder or 0
        button.BackgroundColor3 = Tokens.Color.SurfaceRaised
        button.TextColor3 = Tokens.Color.TextPrimary
        button.TextSize = Tokens.TextSize.Body
        button.Font = Enum.Font.GothamBold
        button.BorderSizePixel = 0
        button.AutoButtonColor = true
        button.Parent = props.Parent or game.Players.LocalPlayer:WaitForChild("PlayerGui")

        local uiCorner = Instance.new("UICorner")
        uiCorner.CornerRadius = UDim.new(0, Tokens.Radius.SM)
        uiCorner.Parent = button

        local uiStroke = Instance.new("UIStroke")
        uiStroke.Color = Tokens.Color.Stroke
        uiStroke.Thickness = Tokens.Stroke.Thin
        uiStroke.Parent = button
        
        if props.Variant then
            if props.Variant == "Accent" then
                button.BackgroundColor3 = Tokens.Color.Accent
            elseif props.Variant == "Danger" then
                button.BackgroundColor3 = Tokens.Color.Danger
            elseif props.Variant == "Success" then
                button.BackgroundColor3 = Tokens.Color.Success
            elseif props.Variant == "Warning" then
                button.BackgroundColor3 = Tokens.Color.Warning
            end
        end

        local unavailable = props.Disabled == true or props.Loading == true
        button.Interactable = not unavailable
        button.Active = not unavailable
        button.Selectable = not unavailable
        button.AutoButtonColor = not unavailable
        if props.Loading then
            button.Text = "WORKING…"
            button.TextColor3 = Tokens.Color.TextSecondary
        elseif props.Disabled then
            button.TextColor3 = Tokens.Color.TextMuted
        end
        button.BackgroundTransparency = if unavailable then Tokens.Transparency.Disabled else Tokens.Transparency.Surface
        
        if props.OnActivated and not unavailable then
            button.Activated:Connect(function()
                props.OnActivated()
            end)
        end
        
        return button
    end,
}
return Button
