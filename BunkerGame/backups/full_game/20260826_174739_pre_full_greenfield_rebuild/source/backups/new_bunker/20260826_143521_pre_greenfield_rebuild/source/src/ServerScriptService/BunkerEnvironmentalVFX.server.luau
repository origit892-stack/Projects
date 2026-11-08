--!strict
-- Restrained environmental VFX for the approved NewBunker art pass.
-- Runtime-only emitters attach to existing authored visual anchors. They do not
-- create collision, gameplay state, interaction affordances, or new geometry.

local Workspace = game:GetService("Workspace")

local STARTUP_DELAY = 1

type VFXContract = {
	anchorName: string,
	emitterName: string,
	texture: string,
	rate: number,
	lifetime: NumberRange,
	speed: NumberRange,
	acceleration: Vector3,
	drag: number,
	spreadAngle: Vector2,
	rotation: NumberRange,
	rotSpeed: NumberRange,
	size: NumberSequence,
	transparency: NumberSequence,
	color: ColorSequence,
	lightInfluence: number,
	orientation: Enum.ParticleOrientation,
}

local contracts: { VFXContract } = {
	{
		anchorName = "WaterDripPool",
		emitterName = "SparseWaterDrip",
		texture = "rbxasset://textures/particles/sparkles_main.dds",
		rate = 1.2,
		lifetime = NumberRange.new(0.32, 0.48),
		speed = NumberRange.new(0.8, 1.35),
		acceleration = Vector3.new(0, -9, 0),
		drag = 0,
		spreadAngle = Vector2.new(5, 5),
		rotation = NumberRange.new(0, 180),
		rotSpeed = NumberRange.new(-20, 20),
		size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.055),
			NumberSequenceKeypoint.new(0.7, 0.035),
			NumberSequenceKeypoint.new(1, 0),
		}),
		transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.36),
			NumberSequenceKeypoint.new(0.75, 0.48),
			NumberSequenceKeypoint.new(1, 1),
		}),
		color = ColorSequence.new(Color3.fromRGB(150, 184, 190), Color3.fromRGB(94, 125, 130)),
		lightInfluence = 0.82,
		orientation = Enum.ParticleOrientation.FacingCamera,
	},
	{
		anchorName = "ServiceWetSheen",
		emitterName = "LowServiceMist",
		texture = "rbxasset://textures/particles/smoke_main.dds",
		rate = 0.55,
		lifetime = NumberRange.new(2.4, 4.0),
		speed = NumberRange.new(0.08, 0.22),
		acceleration = Vector3.new(0, 0.16, 0),
		drag = 0.9,
		spreadAngle = Vector2.new(18, 18),
		rotation = NumberRange.new(0, 360),
		rotSpeed = NumberRange.new(-4, 4),
		size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.45),
			NumberSequenceKeypoint.new(0.55, 0.82),
			NumberSequenceKeypoint.new(1, 1.1),
		}),
		transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.93),
			NumberSequenceKeypoint.new(0.35, 0.88),
			NumberSequenceKeypoint.new(1, 1),
		}),
		color = ColorSequence.new(Color3.fromRGB(104, 121, 117), Color3.fromRGB(74, 88, 86)),
		lightInfluence = 0.9,
		orientation = Enum.ParticleOrientation.FacingCamera,
	},
	{
		anchorName = "ExhaustCap",
		emitterName = "GeneratorExhaustHaze",
		texture = "rbxasset://textures/particles/smoke_main.dds",
		rate = 0.75,
		lifetime = NumberRange.new(1.5, 2.5),
		speed = NumberRange.new(0.28, 0.52),
		acceleration = Vector3.new(0, 0.42, 0),
		drag = 0.65,
		spreadAngle = Vector2.new(10, 10),
		rotation = NumberRange.new(0, 360),
		rotSpeed = NumberRange.new(-7, 7),
		size = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.32),
			NumberSequenceKeypoint.new(0.6, 0.72),
			NumberSequenceKeypoint.new(1, 1.0),
		}),
		transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.88),
			NumberSequenceKeypoint.new(0.45, 0.84),
			NumberSequenceKeypoint.new(1, 1),
		}),
		color = ColorSequence.new(Color3.fromRGB(76, 78, 74), Color3.fromRGB(52, 57, 55)),
		lightInfluence = 0.78,
		orientation = Enum.ParticleOrientation.FacingCamera,
	},
}

local function attachEmitter(anchor: BasePart, contract: VFXContract)
	if anchor:FindFirstChild(contract.emitterName) then
		return
	end

	local attachment = Instance.new("Attachment")
	attachment.Name = contract.emitterName .. "Anchor"
	attachment.Parent = anchor

	local emitter = Instance.new("ParticleEmitter")
	emitter.Name = contract.emitterName
	emitter.Texture = contract.texture
	emitter.Rate = contract.rate
	emitter.Lifetime = contract.lifetime
	emitter.Speed = contract.speed
	emitter.Acceleration = contract.acceleration
	emitter.Drag = contract.drag
	emitter.SpreadAngle = contract.spreadAngle
	emitter.Rotation = contract.rotation
	emitter.RotSpeed = contract.rotSpeed
	emitter.Size = contract.size
	emitter.Transparency = contract.transparency
	emitter.Color = contract.color
	emitter.LightInfluence = contract.lightInfluence
	emitter.Orientation = contract.orientation
	emitter.LockedToPart = false
	emitter.Enabled = true
	emitter.Parent = attachment
end

task.wait(STARTUP_DELAY)

local rebuild = Workspace:WaitForChild("Rebuild", 30)
local bunker = rebuild and rebuild:WaitForChild("NewBunker", 30)
if not bunker then
	warn("[BunkerEnvironmentalVFX] NewBunker was not found; environmental VFX are disabled")
	return
end

for _, contract in contracts do
	local found = 0
	for _, descendant in bunker:GetDescendants() do
		if descendant:IsA("BasePart") and descendant.Name == contract.anchorName then
			attachEmitter(descendant, contract)
			found += 1
		end
	end

	if found == 0 then
		warn(string.format("[BunkerEnvironmentalVFX] Anchor %s was not found", contract.anchorName))
	end
end
