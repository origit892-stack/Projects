-- Prototype tuning values for the first Survival Vertical Slice. Not final balance.
local definitions = {
    axe_basic = table.freeze({
        Id = "axe_basic",
        ToolTags = table.freeze({ Axe = true }),
        HarvestDamage = 25,
        UseCooldownSeconds = 0.55,
    }),
}

local ToolDefinitions = {}

function ToolDefinitions.get(id: string)
    return definitions[id]
end

function ToolDefinitions.getAll()
    return table.clone(definitions)
end

return table.freeze(ToolDefinitions)
