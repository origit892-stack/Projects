local Types = {
    UI = {
        Panel = "Panel",
        Button = "Button",
        StatChip = "StatChip",
        ProgressBar = "ProgressBar",
        Notification = "Notification",
        InteractionPrompt = "InteractionPrompt",
    },
    InteractionFeedback = {
        Success = "Success",
        Unavailable = "Unavailable",
    },
}
return table.freeze(Types)
