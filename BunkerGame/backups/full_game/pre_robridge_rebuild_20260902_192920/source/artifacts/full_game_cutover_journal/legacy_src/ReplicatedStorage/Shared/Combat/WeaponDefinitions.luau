-- Canonical weapon-definition boundary. No weapon content is authorized in FND-003.
local definitions = {}

local WeaponDefinitions = {}

function WeaponDefinitions.get(weaponId: string)
    return definitions[weaponId]
end

function WeaponDefinitions.isDefined(weaponId: string): boolean
    return definitions[weaponId] ~= nil
end

function WeaponDefinitions.getAll()
    return table.clone(definitions)
end

return table.freeze(WeaponDefinitions)
