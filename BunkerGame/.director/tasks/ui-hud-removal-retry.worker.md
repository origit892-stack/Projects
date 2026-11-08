# Worker Task

TASK_ID=ui-hud-removal-retry

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

Complete TASK 1 and TASK 2 from the objective file /Users/Ori/Documents/Projects/BunkerGame/.director/director/objectives/continue-20260928-225559-45115.objective.md against src/StarterPlayer/StarterPlayerScripts/GameClient/UIController.luau. IMPORTANT: the previous worker attempt on this file FAILED with an invalid completion contract and its file changes are UNKNOWN — the file may be unmodified, partially modified, or fully modified. FIRST inspect the current state of UIController.luau (and diff against git if useful) to classify what the prior attempt left behind; do not assume a clean baseline. Then converge the file to the exact required end state: (1) _buildGui keeps only ScreenGui 'OutskirtsHUD' + SafeAreaRoot + the fully intact _buildWeaponsButton (blue gradient tile, rifle, spider webs, spider, white 'Weapons' label, hover/press/bob/web-breath/spider-crawl animations, click notification) plus a minimal Notifications frame only if ShowNotification needs a parent; remove ALL other HUD elements (PhaseReadout, ObjectiveCard, ResourceReadout, SurvivalReadout, EquipmentHotbar, Reticle, TouchPrimary, InteractionPrompt, ConnectionStatus, entire ModalLayer) and all now-dead functions/copy tables listed in the objective that are truly unreferenced after cleanup. (2) Remove the 'Glint' frame creation and its entire sweep block (glint.Visible, glint.Position, TweenService sweep, sweep.Completed handler) from _buildWeaponsButton; KEEP the press animation, hover animation, and the 'Glow' frame. (3) InputController compatibility: SetCallbacks, SetPreferredInput, ShowPrompt, HidePrompt, SetPromptProgress must exist (no-ops where backing UI is gone); IsPointerOverInteractiveUI must return true only when the pointer is over the weapons button; ShowNotification must remain fully working. (4) Keep _reducedMotion detection; simplify Start()/Stop() per the objective while keeping self._refs.WeaponsCleanup invocation in Stop. Do NOT change the weapons button's existing visuals. Do NOT touch any other file. After implementation, verify: GATE 1 — luau-analyze on UIController.luau reports 0 SyntaxErrors (TypeErrors from missing Roblox API definitions outside Studio are acceptable); GATE 2 — weapons button visuals/animations intact, no 'Glint' frame or sweep remains, no active references to removed refs (e.g. self._refs.PhasePanel, self._refs.Hotbar1, self._refs.Modal); GATE 3 — every UI method called by src/StarterPlayer/StarterPlayerScripts/GameClient/InputController.luau still exists. CRITICAL: you MUST emit a valid AGENT_HANDOFF with status, result, files_changed, verification evidence, and blockers — the previous attempt failed solely for a missing/invalid handoff; a successful edit without a valid handoff counts as FAILED.

## Write scopes

["src/StarterPlayer/StarterPlayerScripts/GameClient/UIController.luau"]

## Read scopes

["src", ".director/director/objectives/continue-20260928-225559-45115.objective.md"]

## Acceptance criteria

Valid AGENT_HANDOFF present with: (a) classification of the prior attempt's leftover state before editing; (b) GATE 1 evidence: luau-analyze output showing 0 SyntaxErrors on UIController.luau; (c) GATE 2 evidence: weapons button intact, Glint frame and sweep removed, grep showing no active references to removed refs; (d) GATE 3 evidence: each InputController-called method (SetCallbacks, SetPreferredInput, ShowPrompt, HidePrompt, SetPromptProgress, IsPointerOverInteractiveUI, ShowNotification) present in the file; (e) files_changed lists only src/StarterPlayer/StarterPlayerScripts/GameClient/UIController.luau.

## Rules

Work autonomously until PASS, BLOCKED, or FAILED.
Use your available tools directly.
Do not perform unrelated project work.
Verify before PASS.
Return only the final handoff to the Director.

## Final handoff

<AGENT_HANDOFF>
STATUS=PASS|BLOCKED|FAILED
TASK_ID=<task id>
EXECUTED=<what was performed>
RESULT=<final result>
FILES_CHANGED=<paths or NONE>
ARTIFACTS=<paths/ids or NONE>
VERIFICATION=<objective evidence>
BLOCKERS=<NONE or blocker>
</AGENT_HANDOFF>
