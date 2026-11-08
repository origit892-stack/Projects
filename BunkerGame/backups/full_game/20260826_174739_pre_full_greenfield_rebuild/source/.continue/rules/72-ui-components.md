---
name: BunkerGame UI component contracts
alwaysApply: true
---

# UI Component Contracts

## Panel
`Panel.create(props) -> Frame`

Props: Name, Size, Position, AnchorPoint, LayoutOrder, Parent, Variant, Visible.

## Button
`Button.create(props) -> TextButton`

Props: Name, Text, Size, Position, LayoutOrder, Parent, Disabled, Loading, Variant, OnActivated.

Rules:
- use `Activated`
- `Selectable = true` unless disabled
- disabled/loading prevent duplicate activation
- desktop hover uses MouseEnter/MouseLeave
- gamepad focus uses SelectionGained/SelectionLost
- no duplicate TouchEnded activation

## StatChip
```lua
local chip = StatChip.create(props)
chip:SetValue(value)
chip:SetLabel(text)
chip:Destroy()
```

Phase 1 values only: Credits, Seeds, Crops, FoodItems.

## ProgressBar
```lua
local bar = ProgressBar.create(props)
bar:SetProgress(normalizedValue)
bar:SetLabel(text)
bar:SetVisible(visible)
bar:Destroy()
```

Clamp progress to 0..1. Existing `UpdateProgress` drives farming processing progress.

## Notification
```lua
local notification = Notification.create(props)
notification:Show(text, variant)
notification:Destroy()
```

Variants: Info, Success, Warning, Danger.

Existing `Notify` remains the source of farming notifications during migration.

## Lifecycle
Components that create RBXScriptConnections must clean them up or own Instances whose destruction safely ends them.

The bootstrap/controller owns the root ScreenGui and passes parents to components.
