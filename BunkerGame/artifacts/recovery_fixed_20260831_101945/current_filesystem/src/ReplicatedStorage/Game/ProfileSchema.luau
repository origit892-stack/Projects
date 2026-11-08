--!strict

local Config = require(script.Parent.Config)
local Definitions = require(script.Parent.Definitions)

export type ItemQuantities = { [string]: number }

export type Upgrades = {
    harvest: number,
    weapon: number,
    storage: number,
}

export type Onboarding = {
    Version: number,
    Step: Definitions.OnboardingStep,
    Completed: boolean,
}

export type Stats = {
    HighestDay: number,
    ZombiesDefeated: number,
    TreesHarvested: number,
}

export type ProfileV1 = {
    SchemaVersion: number,
    Revision: number,
    Inventory: ItemQuantities,
    Storage: ItemQuantities,
    Currencies: {
        credits: number,
    },
    Upgrades: Upgrades,
    Onboarding: Onboarding,
    StarterGrantVersions: { [string]: boolean },
    Stats: Stats,
}

export type StoredRecord = {
    Profile: ProfileV1,
    Lock: {
        JobId: string,
        ExpiresAt: number,
    },
}

local PROFILE_KEYS = table.freeze({
    SchemaVersion = true,
    Revision = true,
    Inventory = true,
    Storage = true,
    Currencies = true,
    Upgrades = true,
    Onboarding = true,
    StarterGrantVersions = true,
    Stats = true,
})
local CURRENCY_KEYS = table.freeze({ credits = true })
local UPGRADE_KEYS = table.freeze({ harvest = true, weapon = true, storage = true })
local ONBOARDING_KEYS = table.freeze({ Version = true, Step = true, Completed = true })
local STATS_KEYS = table.freeze({ HighestDay = true, ZombiesDefeated = true, TreesHarvested = true })
local STORED_RECORD_KEYS = table.freeze({ Profile = true, Lock = true })
local LOCK_KEYS = table.freeze({ JobId = true, ExpiresAt = true })

local function asPlainTable(value: unknown): { [any]: any }?
    if type(value) ~= "table" then
        return nil
    end

    local tableValue = value :: { [any]: any }
    if getmetatable(tableValue) ~= nil then
        return nil
    end

    return tableValue
end

local function hasExactKeys(value: { [any]: any }, expected: { [string]: boolean }): boolean
    for key in pairs(value) do
        if type(key) ~= "string" or expected[key] ~= true then
            return false
        end
    end

    for key in pairs(expected) do
        if value[key] == nil then
            return false
        end
    end

    return true
end

local function isFiniteNumber(value: unknown): boolean
    return type(value) == "number"
        and value == value
        and value > -math.huge
        and value < math.huge
end

local function isIntegerInRange(value: unknown, minimum: number, maximum: number): boolean
    return type(value) == "number" and Config.IsIntegerInRange(value, minimum, maximum)
end

local function validateQuantities(
    value: unknown,
    storageTier: number?,
    enforceStorageRules: boolean
): (boolean, string?, number?)
    local quantities = asPlainTable(value)
    if quantities == nil then
        return false, "must be a plain table", nil
    end

    local used = 0
    for rawItemId, rawQuantity in pairs(quantities) do
        if type(rawItemId) ~= "string" or not Definitions.IsItemId(rawItemId) then
            return false, "contains an unknown item ID", nil
        end

        local definition = Definitions.Items[rawItemId]
        if not isIntegerInRange(rawQuantity, 0, definition.StackCap) then
            return false, string.format("quantity for %s is outside 0..%d", rawItemId, definition.StackCap), nil
        end

        if enforceStorageRules and not definition.StorageAllowed and rawQuantity ~= 0 then
            return false, string.format("%s is not storable", rawItemId), nil
        end

        used += rawQuantity
    end

    if enforceStorageRules then
        assert(storageTier ~= nil, "storageTier is required for storage validation")
        local capacity = Config.GetStorageCapacity(storageTier)
        if used > capacity then
            return false, string.format("uses %d units but capacity is %d", used, capacity), nil
        end
    end

    return true, nil, used
end

local function validateProfile(value: unknown): (boolean, string?)
    local profile = asPlainTable(value)
    if profile == nil or not hasExactKeys(profile, PROFILE_KEYS) then
        return false, "Profile must be a plain table with the exact ProfileV1 keys"
    end

    if profile.SchemaVersion ~= Config.Profile.SchemaVersion then
        return false, "Profile.SchemaVersion must equal 1"
    end
    if not isIntegerInRange(profile.Revision, Config.Profile.RevisionMinimum, Config.Profile.RevisionMaximum) then
        return false, "Profile.Revision is outside the frozen range"
    end

    local currencies = asPlainTable(profile.Currencies)
    if currencies == nil or not hasExactKeys(currencies, CURRENCY_KEYS) then
        return false, "Profile.Currencies must contain only credits"
    end
    if not isIntegerInRange(currencies.credits, Config.Profile.CreditsMinimum, Config.Profile.CreditsMaximum) then
        return false, "Profile.Currencies.credits is outside 0..999999"
    end

    local upgrades = asPlainTable(profile.Upgrades)
    if upgrades == nil or not hasExactKeys(upgrades, UPGRADE_KEYS) then
        return false, "Profile.Upgrades must contain the three frozen upgrade IDs"
    end
    for _, upgradeId in ipairs(Definitions.UpgradeIds) do
        if not isIntegerInRange(
            upgrades[upgradeId],
            Config.Profile.UpgradeTierMinimum,
            Config.Profile.UpgradeTierMaximum
        ) then
            return false, string.format("Profile.Upgrades.%s must be 0 or 1", upgradeId)
        end
    end

    local inventoryValid, inventoryError = validateQuantities(profile.Inventory, nil, false)
    if not inventoryValid then
        return false, "Profile.Inventory " .. (inventoryError :: string)
    end

    local storageValid, storageError = validateQuantities(profile.Storage, upgrades.storage, true)
    if not storageValid then
        return false, "Profile.Storage " .. (storageError :: string)
    end

    local onboarding = asPlainTable(profile.Onboarding)
    if onboarding == nil or not hasExactKeys(onboarding, ONBOARDING_KEYS) then
        return false, "Profile.Onboarding has an invalid shape"
    end
    if onboarding.Version ~= Config.Profile.OnboardingVersion then
        return false, "Profile.Onboarding.Version must equal 1"
    end
    if not Definitions.IsOnboardingStep(onboarding.Step) then
        return false, "Profile.Onboarding.Step is unknown"
    end
    if type(onboarding.Completed) ~= "boolean" then
        return false, "Profile.Onboarding.Completed must be boolean"
    end
    if onboarding.Completed ~= (onboarding.Step == "onboarding_complete") then
        return false, "Profile.Onboarding completion and step disagree"
    end

    local grants = asPlainTable(profile.StarterGrantVersions)
    if grants == nil then
        return false, "Profile.StarterGrantVersions must be a plain table"
    end
    for grantId, granted in pairs(grants) do
        if grantId ~= Definitions.StarterGrant.Id or granted ~= true then
            return false, "Profile.StarterGrantVersions contains an unknown or invalid marker"
        end
    end

    local stats = asPlainTable(profile.Stats)
    if stats == nil or not hasExactKeys(stats, STATS_KEYS) then
        return false, "Profile.Stats has an invalid shape"
    end
    for _, statName in ipairs({ "HighestDay", "ZombiesDefeated", "TreesHarvested" }) do
        if not isIntegerInRange(stats[statName], 0, Config.Profile.RevisionMaximum) then
            return false, string.format("Profile.Stats.%s is outside the frozen integer range", statName)
        end
    end

    return true, nil
end

local function validateForConsumer(value: unknown): (boolean, string?)
    local valid = validateProfile(value)
    return valid, if valid then nil else "PROFILE_CONFLICT"
end

local function validateStoredRecord(value: unknown): (boolean, string?)
    local record = asPlainTable(value)
    if record == nil or not hasExactKeys(record, STORED_RECORD_KEYS) then
        return false, "StoredRecord has an invalid shape"
    end

    local profileValid, profileError = validateProfile(record.Profile)
    if not profileValid then
        return false, profileError
    end

    local lock = asPlainTable(record.Lock)
    if lock == nil or not hasExactKeys(lock, LOCK_KEYS) then
        return false, "StoredRecord.Lock has an invalid shape"
    end
    if type(lock.JobId) ~= "string" then
        return false, "StoredRecord.Lock.JobId must be a string"
    end
    if not isFiniteNumber(lock.ExpiresAt) or lock.ExpiresAt < 0 then
        return false, "StoredRecord.Lock.ExpiresAt must be a nonnegative finite timestamp"
    end

    return true, nil
end

local function copyQuantities(source: ItemQuantities): ItemQuantities
    local copy: ItemQuantities = {}
    for itemId, quantity in pairs(source) do
        copy[itemId] = quantity
    end
    return copy
end

local function createDefault(): ProfileV1
    return {
        SchemaVersion = Config.Profile.SchemaVersion,
        Revision = 0,
        Inventory = {},
        Storage = {},
        Currencies = {
            credits = Config.Profile.DefaultCredits,
        },
        Upgrades = {
            harvest = 0,
            weapon = 0,
            storage = 0,
        },
        Onboarding = {
            Version = Config.Profile.OnboardingVersion,
            Step = "wake_in_bunker",
            Completed = false,
        },
        StarterGrantVersions = {},
        Stats = {
            HighestDay = 0,
            ZombiesDefeated = 0,
            TreesHarvested = 0,
        },
    }
end

local function copyProfile(source: ProfileV1): ProfileV1
    local grants: { [string]: boolean } = {}
    for grantId, granted in pairs(source.StarterGrantVersions) do
        grants[grantId] = granted
    end

    return {
        SchemaVersion = source.SchemaVersion,
        Revision = source.Revision,
        Inventory = copyQuantities(source.Inventory),
        Storage = copyQuantities(source.Storage),
        Currencies = {
            credits = source.Currencies.credits,
        },
        Upgrades = {
            harvest = source.Upgrades.harvest,
            weapon = source.Upgrades.weapon,
            storage = source.Upgrades.storage,
        },
        Onboarding = {
            Version = source.Onboarding.Version,
            Step = source.Onboarding.Step,
            Completed = source.Onboarding.Completed,
        },
        StarterGrantVersions = grants,
        Stats = {
            HighestDay = source.Stats.HighestDay,
            ZombiesDefeated = source.Stats.ZombiesDefeated,
            TreesHarvested = source.Stats.TreesHarvested,
        },
    }
end

local function copyStoredRecord(source: StoredRecord): StoredRecord
    return {
        Profile = copyProfile(source.Profile),
        Lock = {
            JobId = source.Lock.JobId,
            ExpiresAt = source.Lock.ExpiresAt,
        },
    }
end

local function getStorageUsed(profile: ProfileV1): number
    local used = 0
    for _, quantity in pairs(profile.Storage) do
        used += quantity
    end
    return used
end

local ProfileSchema = {
    Name = Config.Profile.SchemaName,
    Version = Config.Profile.SchemaVersion,
    DataStoreName = Config.Profile.DataStoreName,
    StarterGrantId = Definitions.StarterGrant.Id,

    CreateDefault = createDefault,
    Copy = copyProfile,
    CopyQuantities = copyQuantities,
    Validate = validateForConsumer,
    ValidateDetailed = validateProfile,
    ValidateStoredRecord = validateStoredRecord,
    CopyStoredRecord = copyStoredRecord,
    GetStorageUsed = getStorageUsed,
    GetStorageCapacity = function(profile: ProfileV1): number
        return Config.GetStorageCapacity(profile.Upgrades.storage)
    end,
    IsStarterGranted = function(profile: ProfileV1): boolean
        return profile.StarterGrantVersions[Definitions.StarterGrant.Id] == true
    end,
}

return table.freeze(ProfileSchema)
