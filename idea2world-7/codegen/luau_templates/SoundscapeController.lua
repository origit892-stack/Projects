-- SoundscapeController: sets up the audible layer without pretending we own audio assets.
-- Roblox audio must be licensed and uploaded; the planner emits slots, not fabricated ids.
local Config = require(script.Parent.MapConfig)

local SoundscapeController = {}

function SoundscapeController.build(parent, progress)
	local SoundService = game:GetService("SoundService")
	local group = SoundService:FindFirstChild("Idea2WorldSoundscape")
	if not group then
		group = Instance.new("SoundGroup")
		group.Name = "Idea2WorldSoundscape"
		group.Volume = 0.55
		group.Parent = SoundService
	end
	local spec = Config.Soundscape or {}
	local folder = SoundService:FindFirstChild("Idea2World_Ambience")
	if folder then
		folder:Destroy()
	end
	folder = Instance.new("Folder")
	folder.Name = "Idea2World_Ambience"
	folder.Parent = SoundService

	local created = 0
	local missingSources = 0
	for _, slot in ipairs(spec.slots or {}) do
		if slot.soundId and slot.soundId ~= "" then
			local sound = Instance.new("Sound")
			sound.Name = slot.id
			sound.SoundId = slot.soundId
			sound.Volume = slot.volume or 0.4
			sound.Looped = true
			sound.SoundGroup = group
			sound.Parent = folder
			sound:Play()
			created += 1
		else
			missingSources += 1
		end
	end
	if progress then
		progress(1, ("sound slots %d"):format(#(spec.slots or {})))
	end
	return { playing = created, awaitingApprovedAudio = missingSources,
		note = "Add licensed audio ids in MapConfig.Soundscape.slots[].soundId" }
end

return SoundscapeController
