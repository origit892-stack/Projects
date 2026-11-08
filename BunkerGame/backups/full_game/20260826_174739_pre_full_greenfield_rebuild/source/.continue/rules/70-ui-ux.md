---
name: Roblox UI and UX standards
globs:
  - "**/*.lua"
  - "**/*.luau"
  - "**/*.json"
alwaysApply: false
---

# Roblox UI and UX Standards

## General principles

- Prefer clear, readable, and consistent interfaces.
- Do not overcrowd screens.
- Prioritize the player's primary action.
- Use consistent spacing, sizing, typography, and interaction patterns.
- Preserve the existing visual language unless a redesign is explicitly requested.
- Avoid decorative elements that reduce readability or usability.

## Layout

- Use scalable layouts with `UDim2`, `UIListLayout`, `UIGridLayout`, `UIPadding`, and constraints where appropriate.
- Avoid hard-coded pixel positioning when responsive layout tools are more suitable.
- Support different screen sizes and aspect ratios.
- Respect safe areas and mobile controls.
- Avoid overlapping core controls, chat, inventory, and platform UI.
- Use clear hierarchy between primary, secondary, and informational elements.

## Typography

- Use a small, consistent set of font sizes.
- Maintain sufficient contrast.
- Avoid excessive text density.
- Keep labels concise.
- Use headings, subheadings, body text, and captions consistently.
- Do not rely on color alone to communicate meaning.

## Interaction

- Buttons must have clear labels or universally understood icons.
- Interactive elements should provide hover, pressed, disabled, and loading states where relevant.
- Prevent duplicate activation from rapid clicks.
- Show feedback after player actions.
- Confirm destructive or expensive actions.
- Disable controls when an action is unavailable.
- Avoid hidden interactions unless the game teaches them clearly.

## Mobile and controller support

- Ensure important controls are usable on touch screens.
- Keep touch targets large enough.
- Avoid placing critical controls near screen edges.
- Support keyboard, mouse, controller, and mobile input when relevant.
- Do not assume hover exists on mobile.
- Ensure controller focus navigation is logical.

## Accessibility

- Maintain readable contrast.
- Avoid communicating state only through color.
- Use icons together with text when meaning may be ambiguous.
- Avoid rapid flashing.
- Allow important information to remain visible long enough to read.
- Prefer simple animations that do not obstruct gameplay.
- Keep critical text legible on small screens.

## Feedback and state

- Show clear loading, success, warning, and error states.
- Progress bars must reflect actual progress.
- Do not display fake completion or success before the server confirms it.
- Client UI should reflect server-authoritative state.
- Handle delayed or failed server responses gracefully.
- Avoid stale UI after respawn, reconnect, or state reset.

## Roblox UI architecture

- Keep presentation logic on the client.
- Keep authoritative game decisions on the server.
- Do not place business logic directly inside UI button callbacks when it can be separated.
- Prefer reusable UI controllers or modules for repeated behavior.
- Disconnect UI event connections when interfaces are destroyed.
- Avoid rebuilding entire interfaces unnecessarily.
- Reuse components for repeated panels, buttons, dialogs, and status displays.

## Visual consistency

When introducing new UI:

1. Inspect existing screens.
2. Match existing spacing, corner radius, strokes, shadows, typography, and animation style.
3. Reuse existing components where possible.
4. Define new patterns only when needed.
5. Document reusable visual tokens if the project adopts a design system.

## Review checklist

When reviewing UI, check:

- Responsiveness
- Mobile usability
- Controller navigation
- Readability
- Visual hierarchy
- Interaction feedback
- Loading and error states
- Server-authoritative synchronization
- Duplicate input protection
- Connection cleanup