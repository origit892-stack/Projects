-- Canonical item-definition registry boundary.
-- FND-002 intentionally defines no gameplay item catalog content.
local definitions = {
    wood = table.freeze({
        Id = "wood",
        Category = "Resource",
        StackPolicy = table.freeze({ Stackable = true }),
        Tags = table.freeze({ "Resource", "Wood" }),
        Presentation = table.freeze({ DisplayName = "Wood" }),
    }),
    axe_basic = table.freeze({
        Id = "axe_basic",
        Category = "Tool",
        StackPolicy = table.freeze({ Stackable = false, MaxQuantity = 1 }),
        Tags = table.freeze({ "Tool", "Axe" }),
        Presentation = table.freeze({ DisplayName = "Axe" }),
        GameplayRef = "axe_basic",
    }),
}

local ItemDefinitions = {}

function ItemDefinitions.get(itemId: string)
    return definitions[itemId]
end

function ItemDefinitions.isDefined(itemId: string): boolean
    return definitions[itemId] ~= nil
end

function ItemDefinitions.getAll()
    return table.clone(definitions)
end

return table.freeze(ItemDefinitions)
