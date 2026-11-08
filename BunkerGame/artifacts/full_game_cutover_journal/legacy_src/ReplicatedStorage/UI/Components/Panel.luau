local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Tokens = require(ReplicatedStorage.UI.Tokens)

local Panel = {
    create = function(props)
        local frame = Instance.new("Frame")
        frame.Name = props.Name or "Panel"
        frame.Size = props.Size or UDim2.new(0, 200, 0, 100)
        frame.Position = props.Position or UDim2.new(0.5, -100, 0.5, -50)
        frame.AnchorPoint = props.AnchorPoint or Vector2.new(0.5, 0.5)
        frame.LayoutOrder = props.LayoutOrder or 0
        frame.BackgroundColor3 = Tokens.Color.Surface
        frame.BackgroundTransparency = Tokens.Transparency.Surface
        frame.BorderSizePixel = 0
        frame.Parent = props.Parent or game.Players.LocalPlayer:WaitForChild("PlayerGui")

        local uiCorner = Instance.new("UICorner")
        uiCorner.CornerRadius = UDim.new(0, Tokens.Radius.SM)
        uiCorner.Parent = frame

        local uiStroke = Instance.new("UIStroke")
        uiStroke.Color = Tokens.Color.Stroke
        uiStroke.Thickness = Tokens.Stroke.Thin
        uiStroke.Parent = frame
        
        if props.Variant then
            if props.Variant == "Accent" then
                frame.BackgroundColor3 = Tokens.Color.Accent
            elseif props.Variant == "Danger" then
                frame.BackgroundColor3 = Tokens.Color.Danger
            elseif props.Variant == "Success" then
                frame.BackgroundColor3 = Tokens.Color.Success
            elseif props.Variant == "Warning" then
                frame.BackgroundColor3 = Tokens.Color.Warning
            elseif props.Variant == "SurfaceRaised" then
                frame.BackgroundColor3 = Tokens.Color.SurfaceRaised
            end
        end
        
        if props.Visible ~= nil then
            frame.Visible = props.Visible
        end
        
        return frame
    end,
}
return Panel
