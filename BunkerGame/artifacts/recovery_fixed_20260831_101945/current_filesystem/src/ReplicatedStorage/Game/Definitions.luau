--!strict

local Config = require(script.Parent.Config)

export type ItemId =
    "axe_basic"
    | "rifle_basic"
    | "ammo_rifle"
    | "wood"
    | "scrap"
    | "battery_cell"
    | "seed_wheat"
    | "crop_wheat"
    | "food_ration"

export type UpgradeId = "harvest" | "weapon" | "storage"
export type OfferId = "battery_1" | "wheat_seed_2" | "rifle_ammo_12" | "ration_1"
export type CropId = "wheat"
export type RecipeId = "food_ration_wheat"
export type ResourceDefinitionId = "tree" | "scrap_cache"
export type ZombieDefinitionId = "zombie_basic"
export type OnboardingStep =
    "wake_in_bunker"
    | "harvest_first_wood"
    | "plant_first_crop"
    | "process_first_food"
    | "restore_bunker_power"
    | "survive_first_night"
    | "onboarding_complete"
export type Phase = "Day" | "Dusk" | "Night" | "Dawn"
export type InteractionKind =
    "farm_plot"
    | "food_processor"
    | "shop"
    | "storage"
    | "power"
    | "scrap_exchange"
    | "upgrade"
export type InteractionAction =
    "FarmPlant"
    | "FarmHarvest"
    | "ProcessorStart"
    | "ShopBuy"
    | "StorageTransfer"
    | "PowerActivate"
    | "ScrapExchange"
    | "UpgradeBuy"

export type ItemDefinition = {
    Id: ItemId,
    StackCap: number,
    Kind: "Tool" | "Ammunition" | "Resource" | "Consumable",
    RuntimeTool: boolean,
    HotbarSlot: number?,
    StorageAllowed: boolean,
}

export type UpgradeDefinition = {
    Id: UpgradeId,
    CreditCost: number,
    MaximumTier: number,
    Effect: "TreeDamage" | "RifleDamage" | "StorageCapacity",
    TierOneValue: number,
}

export type OfferDefinition = {
    Id: OfferId,
    ItemId: ItemId,
    BundleCount: number,
    CreditCost: number,
}

local function deepFreeze<T>(value: T): T
    if type(value) ~= "table" then
        return value
    end

    local tableValue = value :: any
    for _, child in pairs(tableValue) do
        if type(child) == "table" and not table.isfrozen(child) then
            deepFreeze(child)
        end
    end
    table.freeze(tableValue)

    return value
end

local ItemIds: { ItemId } = {
    "axe_basic",
    "rifle_basic",
    "ammo_rifle",
    "wood",
    "scrap",
    "battery_cell",
    "seed_wheat",
    "crop_wheat",
    "food_ration",
}

local Items: { [ItemId]: ItemDefinition } = {
    axe_basic = {
        Id = "axe_basic",
        StackCap = 1,
        Kind = "Tool",
        RuntimeTool = true,
        HotbarSlot = 1,
        StorageAllowed = false,
    },
    rifle_basic = {
        Id = "rifle_basic",
        StackCap = 1,
        Kind = "Tool",
        RuntimeTool = true,
        HotbarSlot = 2,
        StorageAllowed = false,
    },
    ammo_rifle = {
        Id = "ammo_rifle",
        StackCap = 240,
        Kind = "Ammunition",
        RuntimeTool = false,
        HotbarSlot = nil,
        StorageAllowed = true,
    },
    wood = {
        Id = "wood",
        StackCap = 200,
        Kind = "Resource",
        RuntimeTool = false,
        HotbarSlot = nil,
        StorageAllowed = true,
    },
    scrap = {
        Id = "scrap",
        StackCap = 100,
        Kind = "Resource",
        RuntimeTool = false,
        HotbarSlot = nil,
        StorageAllowed = true,
    },
    battery_cell = {
        Id = "battery_cell",
        StackCap = 10,
        Kind = "Resource",
        RuntimeTool = false,
        HotbarSlot = nil,
        StorageAllowed = true,
    },
    seed_wheat = {
        Id = "seed_wheat",
        StackCap = 50,
        Kind = "Resource",
        RuntimeTool = false,
        HotbarSlot = nil,
        StorageAllowed = true,
    },
    crop_wheat = {
        Id = "crop_wheat",
        StackCap = 50,
        Kind = "Resource",
        RuntimeTool = false,
        HotbarSlot = nil,
        StorageAllowed = true,
    },
    food_ration = {
        Id = "food_ration",
        StackCap = 20,
        Kind = "Consumable",
        RuntimeTool = false,
        HotbarSlot = nil,
        StorageAllowed = true,
    },
}

local UpgradeIds: { UpgradeId } = { "harvest", "weapon", "storage" }
local Upgrades: { [UpgradeId]: UpgradeDefinition } = {
    harvest = {
        Id = "harvest",
        CreditCost = 100,
        MaximumTier = 1,
        Effect = "TreeDamage",
        TierOneValue = Config.Gameplay.Tree.UpgradedAxeDamage,
    },
    weapon = {
        Id = "weapon",
        CreditCost = 200,
        MaximumTier = 1,
        Effect = "RifleDamage",
        TierOneValue = Config.Gameplay.Rifle.UpgradedDamage,
    },
    storage = {
        Id = "storage",
        CreditCost = 150,
        MaximumTier = 1,
        Effect = "StorageCapacity",
        TierOneValue = Config.GetStorageCapacity(1),
    },
}

-- This order is the required lexical order for replicated offer arrays.
local OfferIds: { OfferId } = { "battery_1", "ration_1", "rifle_ammo_12", "wheat_seed_2" }
local Offers: { [OfferId]: OfferDefinition } = {
    battery_1 = {
        Id = "battery_1",
        ItemId = "battery_cell",
        BundleCount = 1,
        CreditCost = 20,
    },
    wheat_seed_2 = {
        Id = "wheat_seed_2",
        ItemId = "seed_wheat",
        BundleCount = 2,
        CreditCost = 10,
    },
    rifle_ammo_12 = {
        Id = "rifle_ammo_12",
        ItemId = "ammo_rifle",
        BundleCount = 12,
        CreditCost = 15,
    },
    ration_1 = {
        Id = "ration_1",
        ItemId = "food_ration",
        BundleCount = 1,
        CreditCost = 15,
    },
}

local Crops = {
    wheat = {
        Id = "wheat" :: CropId,
        SeedItemId = "seed_wheat" :: ItemId,
        HarvestItemId = "crop_wheat" :: ItemId,
        GrowthSeconds = Config.Gameplay.Wheat.GrowthSeconds,
        SeedCost = Config.Gameplay.Wheat.SeedCost,
        CropReward = Config.Gameplay.Wheat.CropReward,
        SeedReward = Config.Gameplay.Wheat.SeedReward,
    },
}

local Recipes = {
    food_ration_wheat = {
        Id = "food_ration_wheat" :: RecipeId,
        InputItemId = "crop_wheat" :: ItemId,
        InputQuantity = Config.Gameplay.Processor.CropCost,
        OutputItemId = "food_ration" :: ItemId,
        OutputQuantity = Config.Gameplay.Processor.RationReward,
        DurationSeconds = Config.Gameplay.Processor.DurationSeconds,
        RequiresPower = true,
    },
}

local Resources = {
    tree = {
        Id = "tree" :: ResourceDefinitionId,
        Health = Config.Gameplay.Tree.Health,
        RewardItemId = "wood" :: ItemId,
        RewardQuantity = Config.Gameplay.Tree.WoodReward,
        RespawnSeconds = Config.Gameplay.Tree.RespawnSeconds,
        InteractionRange = Config.Gameplay.Tree.HitRange,
    },
    scrap_cache = {
        Id = "scrap_cache" :: ResourceDefinitionId,
        Health = 1,
        RewardItemId = "scrap" :: ItemId,
        RewardQuantity = Config.Gameplay.ScrapCache.ScrapReward,
        RespawnSeconds = Config.Gameplay.ScrapCache.RespawnSeconds,
        InteractionRange = Config.Gameplay.ScrapCache.CollectRange,
    },
}

local Tools = {
    axe_basic = {
        ItemId = "axe_basic" :: ItemId,
        Slot = 1,
        PrimaryKind = "Axe",
        TreeCooldownSeconds = Config.Gameplay.Tree.HitCooldownSeconds,
        MeleeDamage = Config.Gameplay.AxeMelee.Damage,
        MeleeCooldownSeconds = Config.Gameplay.AxeMelee.CadenceSeconds,
        MeleeRange = Config.Gameplay.AxeMelee.Range,
    },
    rifle_basic = {
        ItemId = "rifle_basic" :: ItemId,
        Slot = 2,
        PrimaryKind = "Rifle",
        AmmoItemId = "ammo_rifle" :: ItemId,
        AmmoPerShot = Config.Gameplay.Rifle.AmmoPerShot,
        BaseDamage = Config.Gameplay.Rifle.BaseDamage,
        UpgradedDamage = Config.Gameplay.Rifle.UpgradedDamage,
        CooldownSeconds = Config.Gameplay.Rifle.CadenceSeconds,
        Range = Config.Gameplay.Rifle.Range,
    },
}

local Zombies = {
    zombie_basic = {
        Id = "zombie_basic" :: ZombieDefinitionId,
        Health = Config.Gameplay.Zombie.Health,
        WalkSpeed = Config.Gameplay.Zombie.WalkSpeed,
        MeleeDamage = Config.Gameplay.Zombie.MeleeDamage,
        MeleeRange = Config.Gameplay.Zombie.MeleeRange,
        MeleeCooldownSeconds = Config.Gameplay.Zombie.MeleeCooldownSeconds,
        AggroRange = Config.Gameplay.Zombie.AggroRange,
        LeashRange = Config.Gameplay.Zombie.LeashRange,
    },
}

local OnboardingSteps: { OnboardingStep } = {
    "wake_in_bunker",
    "harvest_first_wood",
    "plant_first_crop",
    "process_first_food",
    "restore_bunker_power",
    "survive_first_night",
    "onboarding_complete",
}

local Phases: { Phase } = { "Day", "Dusk", "Night", "Dawn" }

local InteractionKinds: { InteractionKind } = {
    "farm_plot",
    "food_processor",
    "shop",
    "storage",
    "power",
    "scrap_exchange",
    "upgrade",
}

local InteractionActions: { InteractionAction } = {
    "FarmPlant",
    "FarmHarvest",
    "ProcessorStart",
    "ShopBuy",
    "StorageTransfer",
    "PowerActivate",
    "ScrapExchange",
    "UpgradeBuy",
}

local DomainEvents = {
    "WorldReady",
    "ProfileReady",
    "ProfileChanged",
    "ProfileLeaving",
    "CharacterSpawned",
    "CharacterDied",
    "ItemAdded",
    "StorageChanged",
    "EquipmentChanged",
    "ToolHit",
    "TreeHarvested",
    "ScrapCollected",
    "ResourceChanged",
    "PlotPlanted",
    "CropHarvested",
    "FoodProcessed",
    "FarmChanged",
    "PurchaseCompleted",
    "UpgradePurchased",
    "PowerActivated",
    "PowerExpired",
    "PlayerDied",
    "ZombieKilled",
    "WaveChanged",
    "NightSurvived",
    "PhaseChanged",
    "OnboardingChanged",
    "InteractionOpened",
}

local StarterGrant = {
    Id = "starter_v1",
    Version = 1,
    Items = {
        axe_basic = 1,
        rifle_basic = 1,
        ammo_rifle = 24,
        seed_wheat = 4,
        battery_cell = 1,
    },
}

local function getByString<T>(source: { [any]: T }, value: unknown): T?
    if type(value) ~= "string" then
        return nil
    end
    return source[value]
end

local function isItemId(value: unknown): boolean
    return getByString(Items, value) ~= nil
end

local function isUpgradeId(value: unknown): boolean
    return getByString(Upgrades, value) ~= nil
end

local function isOfferId(value: unknown): boolean
    return getByString(Offers, value) ~= nil
end

local function isCropId(value: unknown): boolean
    return getByString(Crops, value) ~= nil
end

local function isRecipeId(value: unknown): boolean
    return getByString(Recipes, value) ~= nil
end

local function isResourceDefinitionId(value: unknown): boolean
    return getByString(Resources, value) ~= nil
end

local function isZombieDefinitionId(value: unknown): boolean
    return getByString(Zombies, value) ~= nil
end

local function indexOf<T>(orderedValues: { T }, value: unknown): number?
    for index, candidate in ipairs(orderedValues) do
        if candidate == value then
            return index
        end
    end
    return nil
end

local function createZeroItemQuantities(): { [ItemId]: number }
    local quantities: { [ItemId]: number } = {}
    for _, itemId in ipairs(ItemIds) do
        quantities[itemId] = 0
    end
    return quantities
end

local function isValidItemQuantity(itemId: unknown, quantity: unknown): boolean
    local definition = getByString(Items, itemId)
    if definition == nil or type(quantity) ~= "number" then
        return false
    end
    return Config.IsIntegerInRange(quantity, 0, definition.StackCap)
end

local Definitions = {
    ItemIds = ItemIds,
    Items = Items,
    UpgradeIds = UpgradeIds,
    Upgrades = Upgrades,
    OfferIds = OfferIds,
    Offers = Offers,
    ShopOffers = Offers,
    CropIds = { "wheat" :: CropId },
    Crops = Crops,
    RecipeIds = { "food_ration_wheat" :: RecipeId },
    Recipes = Recipes,
    ResourceDefinitionIds = { "tree" :: ResourceDefinitionId, "scrap_cache" :: ResourceDefinitionId },
    Resources = Resources,
    ToolItemIds = { "axe_basic" :: ItemId, "rifle_basic" :: ItemId },
    Tools = Tools,
    ZombieDefinitionIds = { "zombie_basic" :: ZombieDefinitionId },
    Zombies = Zombies,
    OnboardingSteps = OnboardingSteps,
    Phases = Phases,
    InteractionKinds = InteractionKinds,
    InteractionActions = InteractionActions,
    DomainEvents = DomainEvents,
    StarterGrant = StarterGrant,

    IsItemId = isItemId,
    IsUpgradeId = isUpgradeId,
    IsOfferId = isOfferId,
    IsCropId = isCropId,
    IsRecipeId = isRecipeId,
    IsResourceDefinitionId = isResourceDefinitionId,
    IsZombieDefinitionId = isZombieDefinitionId,
    IsOnboardingStep = function(value: unknown): boolean
        return indexOf(OnboardingSteps, value) ~= nil
    end,
    IsPhase = function(value: unknown): boolean
        return indexOf(Phases, value) ~= nil
    end,
    IsInteractionKind = function(value: unknown): boolean
        return indexOf(InteractionKinds, value) ~= nil
    end,
    IsInteractionAction = function(value: unknown): boolean
        return indexOf(InteractionActions, value) ~= nil
    end,
    GetOnboardingStepIndex = function(value: unknown): number?
        return indexOf(OnboardingSteps, value)
    end,
    CreateZeroItemQuantities = createZeroItemQuantities,
    IsValidItemQuantity = isValidItemQuantity,
    GetStorageCapacity = Config.GetStorageCapacity,
    GetRifleDamage = Config.GetRifleDamage,
    GetTreeDamage = Config.GetTreeDamage,
}

return deepFreeze(Definitions)
