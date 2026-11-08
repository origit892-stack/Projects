local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UI = ReplicatedStorage:WaitForChild("UI")

-- The contextual interaction layer starts independently so an unrelated HUD
-- dependency cannot suppress nearby-world interaction affordances.
local InteractionPromptController = require(UI.Controllers.InteractionPromptController)
InteractionPromptController.start()

-- Phase 2 migration: the approved UI architecture now owns the primary HUD.
-- FarmingUI remains temporarily active only for farming-specific hotbar/progress
-- until its state bindings are fully migrated, but the unified BunkerHUD starts now.
local UIController = require(UI.Controllers.UIController)
UIController.start()
