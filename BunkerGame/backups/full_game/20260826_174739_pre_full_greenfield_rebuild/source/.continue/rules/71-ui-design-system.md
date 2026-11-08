---
name: BunkerGame UI design system
alwaysApply: true
---

# BunkerGame UI Design System

Visual direction: **Industrial Bunker Horror**

The UI must be polished, dark, industrial, unsettling, highly readable, and restrained.

## Approved tokens

```lua
local Tokens = {
    Color = {
        Background = Color3.fromRGB(12, 15, 16),
        Surface = Color3.fromRGB(20, 25, 26),
        SurfaceRaised = Color3.fromRGB(29, 35, 36),
        SurfacePressed = Color3.fromRGB(15, 19, 20),
        TextPrimary = Color3.fromRGB(226, 229, 223),
        TextSecondary = Color3.fromRGB(171, 179, 173),
        TextMuted = Color3.fromRGB(121, 130, 126),
        Accent = Color3.fromRGB(108, 130, 82),
        Machine = Color3.fromRGB(72, 137, 149),
        Warning = Color3.fromRGB(190, 116, 51),
        Danger = Color3.fromRGB(154, 48, 48),
        Success = Color3.fromRGB(76, 133, 82),
        Stroke = Color3.fromRGB(61, 69, 68),
        StrokeStrong = Color3.fromRGB(91, 100, 96),
        Overlay = Color3.fromRGB(0, 0, 0),
    },
    Transparency = {
        Solid = 0,
        Surface = 0.08,
        Muted = 0.32,
        Overlay = 0.28,
        Disabled = 0.48,
    },
    Spacing = { XS = 4, SM = 8, MD = 12, LG = 18, XL = 26, XXL = 36 },
    Radius = { SM = 4, MD = 7, LG = 10 },
    Stroke = { Thin = 1, Normal = 2 },
    TextSize = { Caption = 13, Body = 16, Label = 18, Heading = 24, Display = 32 },
    Motion = { Fast = 0.12, Normal = 0.22, Slow = 0.40, Critical = 0.55 },
    Layer = { HUD = 10, Screen = 30, Modal = 60, Notification = 80, Critical = 100 },
    Input = { MinTouchTarget = 44 },
    Layout = { MaxContentWidth = 1180, CompactBreakpoint = 760 },
}
return table.freeze(Tokens)
```

Use semantic theme roles. Do not hard-code arbitrary visual values inside screens.

Use `Activated` for general button activation.
Do not duplicate activation with `TouchEnded`.
Use `MouseEnter/MouseLeave` only for desktop hover visuals.
Use `SelectionGained/SelectionLost` for gamepad focus.
If `TextScaled` is used, also use `UITextSizeConstraint`.

Horror effects must be restrained: subtle flicker, short glitch, warning pulse, vignette, mechanical transitions. Never run constant glitch/shake.
