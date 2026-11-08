local Theme = {
    Default = {
        Background = "Background",
        Surface = "Surface",
        Text = "TextPrimary",
    },
    Accent = {
        Background = "Accent",
        Text = "TextPrimary",
    },
    Danger = {
        Background = "Danger",
        Text = "TextPrimary",
    },
    Success = {
        Background = "Success",
        Text = "TextPrimary",
    },
    Warning = {
        Background = "Warning",
        Text = "TextPrimary",
    },
    Interaction = {
        Background = "Interaction.Surface",
        Border = "Interaction.SurfaceEdge",
        Accent = "Interaction.Rail",
        Text = "TextPrimary",
        SecondaryText = "TextSecondary",
    },
}
return table.freeze(Theme)
