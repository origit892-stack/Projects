local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Notification = require(ReplicatedStorage.UI.Components.Notification)

local NotificationController = {
    showNotification = function(text, variant)
        local notification = Notification.create({
            Name = "Notification",
            Size = UDim2.new(0, 300, 0, 60),
            Position = UDim2.new(0.5, -150, 0.1, 0),
            AnchorPoint = Vector2.new(0.5, 0),
            Parent = game.Players.LocalPlayer:WaitForChild("PlayerGui"),
            Text = text,
        })
        
        Notification.show(notification, text, variant)

        task.delay(4, function()
            if notification.Parent then
                Notification.destroy(notification)
            end
        end)
    end,
}
return NotificationController
