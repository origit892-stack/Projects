Create a new Luau module for BunkerGame: the Inventory v2 UI. First do bounded discovery: inspect the active src/ tree and project mapping to find where client UI modules live and any existing inventory UI (v1) to match conventions and naming; place the new module in the appropriate client UI folder.

Deliverable: one clean ModuleScript source file, --!strict, returning a module object exposing :Init() and :Mount(parent: ScreenGui). Mount builds the entire Inventory v2 UI procedurally under the given ScreenGui. NO external image/asset IDs: build every layer, gradient, frame, and decoration from built-in instances only (Frame, UIGradient, UIStroke, UICorner, CanvasGroup, TextLabel, UIListLayout, UIPadding, etc.).

SPEC - Bunker Palette, AAA diegetic/tactical look (Escape from Tarkov / The Division / STALKER). Absolutely no flat primitive rectangles.

FRAME AND COLORS:
- Main frame 920x610 px, centered, respects SafeArea.
- Void/Charcoal deep bg #0F151C (transparency 0.05) with a Blur/CanvasGroup layer.
- Panel Steel #1B242E (transparency 0.15) for panels/containers.
- Military Olive #7A8450 tactical highlights.
- Amber Accent #E8A33D for alerts/selection/wear.
- Text: headings #D8DEE6, secondary labels #7F8C9B.

AAA TECHNIQUES:
- Layered depth: every panel = dark bg layer + outer frame layer + inner Inset layer (recessed into metal/charcoal). Never a single flat Frame.
- UIGradient on every surface: subtle vertical (90 deg) 5-10 percent brightness top-to-bottom for real lighting.
- Micro-strokes: UIStroke 1px, transparency 0.4-0.6, #2E3B4B for frames; #E8A33D (transparency 0.2) for selected items.
- UICorner 4-6px only (sharp industrial, not toy-like).
- Tactical texture: 1-2px corner brackets/crosshairs; angular-cut status tags; segmented Weight Bar; segmented load gauge (not a plain progress bar).

LAYOUT:
- Left 60 percent: category tab row (Weapons, Ammo, Gear, Medical, Misc) with a glowing active indicator at the tab bottom; modular slot grid (e.g. 5x4) supporting item sizes 1x1, 1x2, 2x2. AAA slot: dark recessed bg with subtle dot grid or inset frame; embedded corner Stack Badge (dark bg, monospace font); 2px Durability bar with color shift green to yellow to red; subtle Rarity/Tier glow frame.
- Right 40 percent: Inspect Panel - enlarged/model view of item; prominent title with military classification (e.g. MIL-SPEC // RIFLE); segmented data table (Damage, Range, Weight, Fire Rate) with cubic/segmented value bars; description text with clear typography and correct letter spacing; bottom action buttons (Equip, Drop, Inspect, Use) with polished Hover/Press.

ANIMATIONS (TweenService):
- Slot hover: scale 1.02, brighten UIStroke, subtle hover sound (prepare a SoundId hook).
- Slot select: short Amber flash pulse + partial right-panel update via CanvasGroup fade.
- Open/close: smooth vertical slide (Position offset), EasingStyle.Quad, EasingDirection.Out.

Keep it a single self-contained module. The deliverable is the module exposing Init/Mount; do not rewire unrelated game flow.
