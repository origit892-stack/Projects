# OBJECTIVE — Weapons Side-Menu Button (Spider-Web Theme)

## ROLE
You are the autonomous Director. Decompose this into fresh isolated Workers, execute safe non-overlapping Workers in parallel where possible, consume verified handoffs, and continue through fresh cycles until COMPLETE or a genuine BLOCKED. Never convert UNKNOWN/FAILED/BLOCKED/UNVERIFIED into PASS.

## PROJECT ROOT
/Users/Ori/Documents/Projects/BunkerGame

## PRIMARY VISUAL REFERENCE (authoritative)
/Users/Ori/Documents/Projects/BunkerGame/.director/frontdoor/ref/weapons-button-reference.png
(302x686 px crop of a bright-blue vertical side menu. This is the button family to match.)

## CRITICAL CONTEXT — RESOLVE THIS DISCREPANCY FIRST
The current client UI is built by:
  src/StarterPlayer/StarterPlayerScripts/GameClient/UIController.luau
It constructs a ScreenGui named "OutskirtsHUD" (a DARK INDUSTRIAL survival HUD: concrete/steel/sage/amber palette). It does NOT currently contain a bright-blue colorful side menu, and there is NO existing Shop/Store/Inventory/Settings button family in the codebase (verified: no ScreenGui creators other than UIController; no SideMenu/MainMenu/ShopButton symbols).

The reference screenshot is a STYLE reference for the button family. The task is to add ONE new square "Weapons" button that visually belongs to that bright-blue cartoon simulator family, integrated into the EXISTING Roblox UI architecture (the OutskirtsHUD ScreenGui built by UIController). Do NOT rebuild or destroy the existing dark HUD. Do NOT create a separate modern UI. Add the Weapons button as a new self-contained element within the existing UIController ScreenGui, reusing its helpers (create, addCorner, addStroke, label) and its lifecycle (Start/Stop, _connections, _dynamicConnections, _refs).

## EXTRACTED REFERENCE SPECS (measured from the PNG — use as targets)
- Menu background (behind buttons): slate blue-gray ~ Color3.fromRGB(98,108,128).
- Button shape: SQUARE. Measured ~118px wide (x 11..129) and ~118px tall in the 302px-wide crop. In Roblox UI use a square of ~120x120 px (scale to viewport; keep it a true square).
- Corner radius: rounded, ~10-12 px (UDim.new(0, 11) is a good target).
- Outline: THICK dark/near-black border around the ENTIRE button. Measured ~2px in the crop but visually heavy; use UIStroke ApplyStrokeMode=Border, Color ~ Color3.fromRGB(10,12,16), Thickness ~4-5 px for the chunky cartoon look (the crop is low-res; the intent is a bold dark outline).
- Blue gradient (top->bottom): bright cyan-blue at top ~ Color3.fromRGB(70,135,240) down to deep royal blue at bottom ~ Color3.fromRGB(20,35,196). Implement with a UIGradient (ColorSequence) on the button frame, or a vertical gradient ImageLabel. Top should read brighter/cyan, bottom deep royal.
- Glossy/cartoon: subtle inner highlight — a soft white translucent rounded highlight across the top ~40% of the button (e.g. a Frame with UICorner + a vertical white->transparent gradient, ~15-25% opacity), giving a glossy top sheen.
- Visual weight: chunky, colorful, polished Roblox simulator style. The button must read as a bold, saturated, playful tile.

## MAIN ICON — STYLIZED ASSAULT RIFLE (center)
- A large, clearly recognizable stylized assault rifle in clean SIDE/PROFILE view (barrel pointing left or right, stock on the opposite end).
- Cartoon Roblox aesthetic, NOT photorealistic.
- Dark gray/black weapon body (Color3.fromRGB(30,32,36) to Color3.fromRGB(55,58,64)) with lighter metallic highlights (Color3.fromRGB(120,128,140)) so it stays readable against the blue.
- The rifle must occupy MOST of the button interior without touching the edges (leave ~12-16px padding inside the outline).
- Build the rifle PROCEDURALLY from Roblox UI objects (Frames with UICorner) so it is crisp and scalable: e.g. a main receiver body (horizontal rounded frame), a barrel (longer thin frame extending one side), a magazine (angled/vertical frame below the receiver), a stock (frame at the rear), a small grip, and a sight. Compose these as children of a single "Rifle" Frame so the whole rifle can be bobbed/animated as one unit. Do NOT require an external image asset. (If a single ImageLabel with a base64/roblox asset is cleaner, that is acceptable, but procedural Frames are preferred for crispness and to avoid asset dependencies.)

## SPIDER-WEB THEME
- Thin, semi-transparent white/silver spider webs growing from the CORNERS of the button (all four corners, or at least top-left + bottom-right for asymmetry).
- Webs must be SUBTLE so the rifle remains the focal point (low opacity, thin strands).
- Add a few tiny web strands extending behind and partially around the rifle.
- Optional: a tiny cartoon spider hanging from one web strand (small dark body + a couple of legs, built from small Frames/Circles).
- Build webs PROCEDURALLY with Roblox UI objects: thin Frames (1-2px) rotated to form radial spokes from a corner, plus 1-2 concentric arc segments (approximated with short rotated frames or a thin ImageLabel). Keep strand count low (e.g. 4-6 spokes per corner) for subtlety.

## ANIMATIONS (smooth, playful, polished, never distracting)
1. Web idle cycle: web strands slowly appear/expand from the corners, then subtly retract, and repeat (a gentle breathing loop). Use TweenService on the web container's Size/Transparency, or per-strand scale, on a repeating loop (e.g. ~4-6s period).
2. Spider: occasionally crawls a short distance along one strand (a small position tween triggered every ~6-10s, moving a few px and back).
3. Rifle idle: very subtle floating/bobbing (a few px vertical sine bob, ~2-3s period, small amplitude ~3-4px). Respect ReducedMotion (GuiService.ReducedMotionEnabled) — disable or greatly reduce idle motion when enabled.
4. Hover: slightly enlarge the ENTIRE button (e.g. 1.0 -> 1.05) and increase brightness (brighten the gradient / reduce a darkening overlay). Use MouseEnter/MouseLeave + TweenService.
5. Click: quickly compress the button (e.g. 1.0 -> 0.92) then bounce back to normal (use a Back/Quad easing for the bounce). Trigger on Activated.
6. Post-click glint: a brief shine/glint moving across the rifle after clicking (a thin white diagonal highlight Frame that tweens across the rifle area once, ~0.4s, then hides).
- All animations must be driven by TweenService and/or a Heartbeat loop, and must be cleaned up on Stop() (disconnect connections, cancel tweens, destroy created instances). Respect the existing _connections/_dynamicConnections cleanup pattern.

## LABEL — "Weapons"
- Under/overlapping the BOTTOM edge of the square button, add the text "Weapons".
- Large, rounded, BOLD white letters (Font = Enum.Font.GothamBlack or GothamBold; TextColor3 = white).
- VERY THICK black outline/drop shadow (use a UIStroke on the TextLabel with a thick black border, or a TextLabel with a dark shadow via a duplicated offset label; target a bold cartoon outline).
- Match the typography and placement of the reference labels (white bold text sitting just below/overlapping the button's bottom edge, centered on the button).

## INTEGRATION REQUIREMENTS
- Add the Weapons button to the existing OutskirtsHUD ScreenGui inside UIController.luau (or a new module required by UIController, e.g. a WeaponsButton module under GameClient, wired into UIController:Start/Stop). Reuse the existing helpers and lifecycle. Keep it as a left-edge vertical side-menu element (position it on the left side of the screen, vertically centered or upper area, so it reads as a side menu). It must not overlap/break the existing HUD panels (PhaseReadout top-left, ResourceReadout top-right, SurvivalReadout bottom-left, EquipmentHotbar bottom-center, InteractionPrompt, ModalLayer).
- The button should be interactive (a TextButton or Frame with input handling). On click, it may fire a callback (e.g. a Weapons/Inventory intent) — but if no server contract exists for a "weapons" action, wire it to a safe no-op or a notification so it does not error. Do NOT invent server remotes. Keep the click purely client-side visual + optional notification.
- Preserve all existing behavior and public/network/data contracts. This is an additive UI change.

## VERIFICATION (required — do not claim PASS without it)
- Syntax/compile: run the project's Luau syntax check on any changed/new .luau files (e.g. `luau --compile` or the project's existing validation). Report the exact command and output.
- Runtime: verify in Roblox Studio (or the project's established runtime/Studio verification path) that: the button renders with the blue gradient + dark outline + glossy highlight; the rifle is centered and readable; the webs render from corners; hover enlarges+brightens; click compresses+bounces and triggers the glint; the rifle bobs; the spider crawls; the "Weapons" label renders with a thick outline. Capture runtime evidence (Studio screenshot or hierarchy readback) and save it under .director/ or visual-qa/.
- If runtime/Studio verification is NOT possible in this environment, report it as UNVERIFIED (not PASS) and state exactly what was and was not verified.

## CONSTRAINTS
- Do NOT use Terrain:Clear or any destructive terrain op (not relevant here, but do not touch terrain).
- Do NOT perform destructive Git ops. Do NOT force-push.
- Do NOT destroy the existing dark HUD or unrelated UI.
- Do NOT fabricate PASS. Classify every important conclusion as VERIFIED_FACT / INFERENCE / UNKNOWN / STALE_OR_CONFLICTING.
- Keep the change the smallest coherent thing that satisfies the objective.

## DELIVERABLES
1. The Weapons button implemented in the existing UI (source under src/).
2. Procedural rifle + spider-web + animations (Roblox UI objects / Tweens).
3. "Weapons" label matching the reference typography/placement.
4. Syntax/compile validation output.
5. Runtime verification evidence (or an explicit UNVERIFIED statement with reasons).
6. A short completion report listing files changed, what was verified, and any UNKNOWN/UNVERIFIED items.
