-- Prototype tuning values for the first Survival Vertical Slice. Not final balance.
local definitions = {
    tree_basic = table.freeze({
        Id = "tree_basic",
        RequiredToolTag = "Axe",
        MaxHealth = 100,
        RewardItemId = "wood",
        RewardQuantity = 3,
        RespawnDelaySeconds = 8,
        InteractionDistance = 12,
        HitCooldownSeconds = 0.55,
    }),
}

local ResourceDefinitions = {}

function ResourceDefinitions.get(id: string)
    return definitions[id]
end

function ResourceDefinitions.getAll()
    return table.clone(definitions)
end

return table.freeze(ResourceDefinitions)
