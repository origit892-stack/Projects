--!strict

-- These are the only bunker-compatible audio assets verified as loaded in the
-- current Studio place. Keeping playback policy beside the IDs prevents world
-- interaction code from copying legacy Sound instances or relying on unknown
-- assets. Ambient and UI cues intentionally remain absent until validated.

local BunkerAudioCatalog = {
	MetalHingeOpen = table.freeze({
		soundId = "rbxassetid://157167203",
		volume = 0.24,
		playbackSpeedMinimum = 0.96,
		playbackSpeedMaximum = 1.02,
		rollOffMinDistance = 4,
		rollOffMaxDistance = 28,
	}),
	MetalHingeClose = table.freeze({
		soundId = "rbxassetid://157167205",
		volume = 0.22,
		playbackSpeedMinimum = 0.96,
		playbackSpeedMaximum = 1.02,
		rollOffMinDistance = 4,
		rollOffMaxDistance = 28,
	}),
}

return table.freeze(BunkerAudioCatalog)
