# Roblox UI/GUI Design Skills (Professional Guide)

## Core Principles

1. **Clarity over decoration** — Every element must communicate its purpose instantly
2. **Less is more** — Show only what players need at any moment
3. **Consistency** — Same fonts, colors, corner radii, spacing throughout
4. **Accessibility** — Don't rely on color alone; use icons + shapes + animations

## Visual Hierarchy

| Priority | Location | Elements |
|----------|----------|----------|
| Critical | Center screen | Alerts, level-ups, warnings (appear briefly, then disappear) |
| High | Top corners | Health, currency, level, score (persistent status) |
| Medium | Bottom center | Action buttons, abilities, tool selectors (tappable area) |
| Low | Sides | Peripheral info (player list, minimap) |

**Rules:**
- Use **bright colors** for important elements, **muted shades** for less significant ones
- Larger = perceived as more important
- Elements with ample **negative space** draw attention
- **Grouped elements** imply connection
- **Movement** draws attention (animated buttons, particle effects) — use sparingly

## Layout: Scale vs Offset

### Always use Scale for sizing and positioning
```lua
-- RESPONSIVE (works on all screens)
panel.Size = UDim2.fromScale(0.4, 0.6)
panel.Position = UDim2.fromScale(0.5, 0.5)

-- AVOID: breaks on mobile/4K
panel.Size = UDim2.fromOffset(400, 600)
```

### When to use Offset
- Pixel-perfect icons/graphics that would stretch
- Elements that need consistent pixel size (e.g., top bar indicators)
- UIStroke (doesn't support scale natively)

### Combine Scale + Offset for small screens
```lua
-- Scale for proportion, Offset for minimum pixel size
frame.Size = UDim2.new(0.083, 300, 0.002, 300)
-- Works on both PC (scale dominates) and mobile (offset provides minimum)
```

## AnchorPoint & Positioning

```lua
-- Always center with AnchorPoint = 0.5, 0.5
panel.AnchorPoint = Vector2.new(0.5, 0.5)
panel.Position = UDim2.fromScale(0.5, 0.5)

-- Bottom-right corner
panel.AnchorPoint = Vector2.new(1, 1)
panel.Position = UDim2.fromScale(1, 1)
```

**Without AnchorPoint**, position = top-left corner of the element. With `0.5, 0.5`, position = center of the element.

## Responsive UI Pattern (Container Frame)

```lua
-- ALWAYS create a container frame under ScreenGui
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "GameUI"
screenGui.IgnoreGuiInset = true
screenGui.Parent = player.PlayerGui

local container = Instance.new("Frame")
container.Name = "Container"
container.Size = UDim2.fromScale(1, 1)
container.BackgroundTransparency = 1
container.Parent = screenGui

-- Now all children size relative to screen
```

## Size Modifiers & Constraints

### UIAspectRatioConstraint (prevents stretching)
```lua
local constraint = Instance.new("UIAspectRatioConstraint")
constraint.AspectRatio = 1 -- 1:1 for square, 1.5 for 3:2
constraint.DominantAxis = Enum.DominantAxis.Width
constraint.Parent = squareButton
```

### UISizeConstraint (min/max size)
```lua
local sizeConstraint = Instance.new("UISizeConstraint")
sizeConstraint.MinSize = Vector2.new(44, 44) -- mobile touch target
sizeConstraint.MaxSize = Vector2.new(200, 200)
sizeConstraint.Parent = button
```

### UITextSizeConstraint (cap text size)
```lua
local textCap = Instance.new("UITextSizeConstraint")
textCap.MaxTextSize = 24
textCap.MinTextSize = 12
textCap.Parent = textLabel
```

### UIScale (scale everything proportionally)
```lua
local scale = Instance.new("UIScale")
scale.Scale = 0.8 -- shrink entire subtree for mobile
scale.Parent = container
```

### AutomaticSize (content-driven)
```lua
frame.AutomaticSize = Enum.AutomaticSize.Y -- grow vertically with content
```

## Touch Targets (Mobile)

- **Minimum 44x44 points** for tappable buttons
- Detect mobile: `UserInputService.TouchEnabled`
- Apply size multiplier (1.3-1.5x) for mobile:
```lua
local function adjustForMobile(gui: ScreenGui)
    local touchEnabled = UserInputService.TouchEnabled
    local multiplier = if touchEnabled then 1.4 else 1.0

    for _, descendant in gui:GetDescendants() do
        if descendant:IsA("GuiButton") then
            local currentSize = descendant.Size
            descendant.Size = UDim2.new(
                currentSize.X.Scale * multiplier,
                currentSize.X.Offset * multiplier,
                currentSize.Y.Scale * multiplier,
                currentSize.Y.Offset * multiplier
            )
        end
    end
end
```

## Safe Zones & Screen Insets

```lua
-- Respect Roblox top bar and mobile notches
screenGui.ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets

-- Never place interactive elements within 48px of edges on mobile
-- Danger zones: bottom-left (joystick), bottom-right (jump button), top (Roblox bar)
```

## StyleQuery (New Responsive System — 2026)

StyleQuery is Roblox's CSS-like responsive system. It automatically adapts UI based on viewport size, input type, and accessibility settings — **no scripts needed**.

### Built-in Selectors
| Selector | Triggers when |
|----------|--------------|
| `@ViewportDisplaySizeSmall` | Small screen |
| `@ViewportDisplaySizeMedium` | Medium screen |
| `@ViewportDisplaySizeLarge` | Large screen |
| `@PreferredInputKeyboard` | Keyboard/mouse input |
| `@PreferredInputTouch` | Touch input |
| `@PreferredInputGamepad` | Gamepad input |
| `@ReducedMotionEnabled` | User has reduced motion enabled |
| `@PreferredTextSizeMedium/Large/Larger/Largest` | User text size preference |

### Usage
1. Parent a `StyleQuery` to any `GuiBase2d` element
2. Set conditions (MinSize, MaxSize, AspectRatio, or global queries)
3. Use the query name as a selector in StyleRules
4. Styles apply automatically when conditions are met

## Color Theme

### Palette (max 3 colors)
```lua
local Theme = {
    -- Primary (headers, active tabs, confirm buttons)
    Primary = Color3.fromRGB(0, 200, 80),

    -- Neutral (backgrounds, surfaces)
    Background = Color3.fromRGB(18, 18, 24),
    Surface = Color3.fromRGB(28, 28, 38),
    SurfaceLight = Color3.fromRGB(38, 38, 50),

    -- Accent (warnings, errors, highlights)
    Accent = Color3.fromRGB(255, 180, 0),
    Error = Color3.fromRGB(255, 60, 60),

    -- Text
    Text = Color3.fromRGB(240, 240, 245),
    TextDim = Color3.fromRGB(150, 150, 160),
}
```

### Typography
- **GothamBold** for headers — most widely used, renders clearly at all sizes
- **GothamMedium** for body text
- Max 2 font families total
- Avoid: script fonts, decorative fonts, thin strokes
- Minimum 14-18px for body text on mobile

### Contrast
- White text on dark panels OR dark text on light panels
- **Never** place text over busy backgrounds without a solid backing panel
- Test with game running behind UI

## Animations (TweenService)

```lua
local TweenService = game:GetService("TweenService")

-- Menu open/close: 0.2-0.3s
local menuIn = TweenService:Create(
    menuFrame,
    TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
    {Position = UDim2.fromScale(0.5, 0.5)}
)
menuIn:Play()

-- Button press: 0.1s scale down
local function onButtonPress(button)
    local originalSize = button.Size
    local pressSize = UDim2.new(
        originalSize.X.Scale * 0.95,
        originalSize.X.Offset,
        originalSize.Y.Scale * 0.95,
        originalSize.Y.Offset
    )
    local press = TweenService:Create(button, TweenInfo.new(0.1), {Size = pressSize})
    local release = TweenService:Create(button, TweenInfo.new(0.1), {Size = originalSize})
    press:Play()
    press.Completed:Wait()
    release:Play()
end

-- Number animation (counting up/down)
local function animateNumber(label: TextLabel, from: number, to: number, duration: number)
    local start = tick()
    while tick() - start < duration do
        local alpha = (tick() - start) / duration
        label.Text = tostring(math.round(from + (to - from) * alpha))
        RunService.Heartbeat:Wait()
    end
    label.Text = tostring(to)
end
```

**Rules:**
- Button press: 0.1s
- Menu transitions: 0.2-0.3s
- Use `EasingStyle.Quad` or `EasingStyle.Back` for natural feel
- Don't animate too many elements simultaneously (performance)

## Common UI Patterns

### Health Bar
```lua
local healthBar = Instance.new("Frame")
healthBar.Name = "HealthBar"
healthBar.Size = UDim2.new(0.3, 0, 0, 20)
healthBar.Position = UDim2.new(0.35, 0, 0.9, 0)
healthBar.BackgroundColor3 = Theme.Surface
healthBar.Parent = container

local fill = Instance.new("Frame")
fill.Name = "Fill"
fill.Size = UDim2.new(1, 0, 1, 0)
fill.BackgroundColor3 = Theme.Primary
fill.Parent = healthBar

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 4)
corner.Parent = healthBar

humanoid.HealthChanged:Connect(function()
    local ratio = humanoid.Health / humanoid.MaxHealth
    TweenService:Create(fill, TweenInfo.new(0.2), {
        Size = UDim2.new(ratio, 0, 1, 0),
        BackgroundColor3 = if ratio > 0.5 then Theme.Primary
            elseif ratio > 0.25 then Theme.Accent
            else Theme.Error
    }):Play()
end)
```

### Tooltip
```lua
local function showTooltip(parent, text)
    local tooltip = Instance.new("TextLabel")
    tooltip.Name = "Tooltip"
    tooltip.Size = UDim2.fromScale(0, 0)
    tooltip.AutomaticSize = Enum.AutomaticSize.XY
    tooltip.Position = UDim2.new(0.5, 0, 0, -10)
    tooltip.AnchorPoint = Vector2.new(0.5, 1)
    tooltip.BackgroundColor3 = Theme.Background
    tooltip.Text = text
    tooltip.TextColor3 = Theme.Text
    tooltip.TextSize = 14
    tooltip.Font = Enum.Font.GothamMedium
    tooltip.Parent = parent

    TweenService:Create(tooltip, TweenInfo.new(0.2), {
        Size = UDim2.fromScale(0, 0)
    }):Play()
end
```

### Tab Navigation
```lua
-- One menu at a time — close others when opening
local function openMenu(menuName: string)
    for name, menu in menus do
        menu.Visible = (name == menuName)
    end
end
```

## Common Mistakes

1. **Offset instead of Scale** — breaks on mobile (60%+ of players)
2. **TextScaled without UITextSizeConstraint** — text becomes huge on large screens
3. **No container frame** — children don't scale relative to screen
4. **No UIAspectRatioConstraint** — square elements stretch on different aspect ratios
5. **Hover-dependent interactions** — mobile can't hover; need tap alternative
6. **Overlapping menus** — one menu at a time
7. **No loading states** — buttons should show feedback while processing
8. **Inconsistent close button placement** — always top-right, same position in every menu
9. **Ignoring ScreenInsets** — UI gets clipped by mobile notches
10. **No touch target sizing** — buttons < 44px are impossible to tap

## Testing

1. **Device Emulator** — Test tab → Device → select Phone, Tablet, Desktop, Console
2. **Actual Resolution** — toggle "Actual Resolution" in emulator dropdown
3. **Test on real devices** — emulator isn't perfect
4. **Check all platforms** — PC, mobile (iOS + Android), Xbox, VR
5. **Stress test** — open/close menus rapidly, switch orientations

## Roblox Platform UI Zones

| Zone | Location | Notes |
|------|----------|-------|
| Top Bar | Top of screen | 36px height, expands for system features |
| Chat | Top-left | Expandable by player |
| Leaderboard | Top-right | Expandable by player |
| Mobile Controls | Bottom-left | Joystick area |
| Jump Button | Bottom-right | Touch area |
| Dynamic Island | Varies | iPhone 14+ camera cutout |

Set `ScreenGui.ScreenInsets = CoreUISafeInsets` to auto-respect all zones.

## References

- [UI/UX Design Docs](https://create.roblox.com/docs/production/game-design/ui-ux-design)
- [Adaptive Design Guidelines](https://create.roblox.com/docs/en-us/production/publishing/adaptive-design.md)
- [Size Modifiers & Constraints](https://create.roblox.com/docs/en-us/ui/size-modifiers.md)
- [StyleQuery (2026)](https://devforum.roblox.com/t/full-release-stylequery-more-styling-features/4566519)
- [Designing UI Tips](https://devforum.roblox.com/t/designing-ui-tips-and-best-practices/3074034)
- [Roblox UI Scaling Guide](https://devforum.roblox.com/t/complete-comprehensive-roblox-ui-scaling-guide/2232510)