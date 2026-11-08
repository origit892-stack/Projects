local InteractionTypes = {
	InteractiveRootName = "InteractiveProps",

	PromptNames = table.freeze({
		Crate = "PrototypeCratePrompt",
		Locker = "PrototypeLockerPrompt",
		OfflineControl = "OfflineControlPrompt",
		InspectStation = "InspectStationPrompt",
	}),

	FeedbackTone = table.freeze({
		Success = "Success",
		Unavailable = "Unavailable",
	}),

	PartNames = table.freeze({
		MovingPart = "MovingPart",
		OpenPose = "OpenPose",
	}),
}

return table.freeze(InteractionTypes)
