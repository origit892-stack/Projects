--!strict

export type RateLimit = {
    Burst: number,
    RefillPerSecond: number,
}

local MAX_SIGNED_32 = 2_147_483_647

local function isIntegerInRange(value: number, minimum: number, maximum: number): boolean
    return value == value
        and value > -math.huge
        and value < math.huge
        and math.floor(value) == value
        and value >= minimum
        and value <= maximum
end

local function getWaveBudget(day: number, sampledPlayers: number): number
    assert(isIntegerInRange(day, 1, MAX_SIGNED_32), "day must be a positive 32-bit integer")
    assert(isIntegerInRange(sampledPlayers, 1, 6), "sampledPlayers must be between 1 and 6")

    return math.min(18, 3 + day + 2 * (sampledPlayers - 1))
end

local function getStorageCapacity(storageTier: number): number
    assert(isIntegerInRange(storageTier, 0, 1), "storageTier must be 0 or 1")
    return 80 + 40 * storageTier
end

local function getRifleDamage(weaponTier: number): number
    assert(isIntegerInRange(weaponTier, 0, 1), "weaponTier must be 0 or 1")
    return if weaponTier == 1 then 34 else 24
end

local function getTreeDamage(harvestTier: number): number
    assert(isIntegerInRange(harvestTier, 0, 1), "harvestTier must be 0 or 1")
    return if harvestTier == 1 then 2 else 1
end

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

local Config = {
    ProtocolVersion = 1,

    Server = {
        MaxActivePlayers = 6,
        CharacterAutoLoads = false,
        StreamingEnabled = false,
        FriendlyFire = false,
        RespawnDelaySeconds = 8,
        SpawnProtectionSeconds = 10,
    },

    Profile = {
        SchemaName = "ProfileV1",
        SchemaVersion = 1,
        DataStoreName = "FullGameProfiles_v1",
        RecordKeyPrefix = "player:",
        RevisionMinimum = 0,
        RevisionMaximum = MAX_SIGNED_32,
        CreditsMinimum = 0,
        CreditsMaximum = 999_999,
        UpgradeTierMinimum = 0,
        UpgradeTierMaximum = 1,
        DefaultCredits = 25,
        OnboardingVersion = 1,
    },

    Persistence = {
        LoadDeadlineSeconds = 30,
        LoadMaximumAttempts = 5,
        LoadBackoffSeconds = { 0.5, 1, 2, 4, 8 },
        LockLeaseSeconds = 120,
        LockRenewIntervalSeconds = 45,
        AutosaveIntervalSeconds = 60,
        AutosaveJitterSeconds = 5,
        ShutdownDeadlineSeconds = 25,
        StudioUsesMemoryRepositoryByDefault = true,
    },

    Inventory = {
        BaseStorageCapacity = 80,
        StorageCapacityPerTier = 40,
    },

    Gameplay = {
        Tree = {
            Health = 3,
            WoodReward = 4,
            RespawnSeconds = 60,
            HitRange = 10,
            HitCooldownSeconds = 0.55,
            BaseAxeDamage = 1,
            UpgradedAxeDamage = 2,
        },
        ScrapCache = {
            ScrapReward = 2,
            RespawnSeconds = 45,
            CollectRange = 10,
        },
        Wheat = {
            GrowthSeconds = 45,
            CropReward = 2,
            SeedReward = 1,
            SeedCost = 1,
        },
        Processor = {
            CropCost = 2,
            RationReward = 1,
            DurationSeconds = 8,
            MaximumActiveJobsPerPlayer = 1,
        },
        FoodRation = {
            Heal = 35,
            CooldownSeconds = 3,
        },
        Rifle = {
            BaseDamage = 24,
            UpgradedDamage = 34,
            CadenceSeconds = 0.28,
            Range = 180,
            AmmoPerShot = 1,
            UsesMagazine = false,
            UsesReload = false,
            UsesSpread = false,
        },
        AxeMelee = {
            Damage = 18,
            CadenceSeconds = 0.65,
            Range = 8,
        },
        Zombie = {
            Health = 80,
            WalkSpeed = 7,
            MeleeDamage = 10,
            MeleeRange = 4.5,
            MeleeCooldownSeconds = 1.2,
            UpdateFrequencyHz = 5,
            UpdateIntervalSeconds = 0.2,
            PathRecomputeMinimumSeconds = 1,
            AggroRange = 220,
            LeashRange = 300,
            SpawnCadenceSeconds = 1.2,
            ActiveCap = 18,
            KillCreditWindowSeconds = 10,
            KillCredits = 4,
            KillScrap = 1,
        },
        Time = {
            PhaseOrder = { "Day", "Dusk", "Night", "Dawn" },
            DaySeconds = 180,
            DuskSeconds = 20,
            NightSeconds = 150,
            DawnSeconds = 20,
        },
        Wave = {
            ActiveCap = 18,
            BaseBudget = 3,
            BudgetPerDay = 1,
            BudgetPerAdditionalPlayer = 2,
            WavesPerNight = 1,
        },
        Power = {
            BatteryCost = 1,
            DurationSeconds = 180,
            StartsActive = false,
        },
        Economy = {
            ScrapCreditsEach = 5,
            ScrapExchangeMinimum = 1,
            ScrapExchangeMaximum = 20,
            ShopBundleCountMinimum = 1,
            ShopBundleCountMaximum = 5,
        },
    },

    Network = {
        RequestIdMinimumLength = 1,
        RequestIdMaximumLength = 36,
        CanonicalIdMinimumLength = 1,
        CanonicalIdMaximumLength = 48,
        StationTokenLength = 32,
        DefaultCountMinimum = 1,
        DefaultCountMaximum = 50,
        InteractionTokenLifetimeSeconds = 10,
        InteractionMaximumDistance = 12,
        ResultCacheSizePerPlayer = 64,
        ResultCacheLifetimeSeconds = 30,
        SnapshotRetryMinimumSeconds = 0.5,
        SnapshotRetryMaximumSeconds = 5,
        AimMagnitudeMinimum = 0.99,
        AimMagnitudeMaximum = 1.01,
        RateLimits = {
            GetSnapshot = { Burst = 2, RefillPerSecond = 0.5 },
            ToolIntent = { Burst = 12, RefillPerSecond = 6 },
            InteractionIntent = { Burst = 6, RefillPerSecond = 3 },
            InteractionCloseIntent = { Burst = 6, RefillPerSecond = 3 },
            UseItemIntent = { Burst = 3, RefillPerSecond = 1 },
        },
    },

    Performance = {
        GameWorldMaximumBaseParts = 2_500,
        GameWorldMaximumDescendants = 3_600,
        BunkerMaximumBaseParts = 600,
        BunkerMaximumDescendants = 900,
        FarmMaximumBaseParts = 180,
        FarmMaximumCollidableParts = 40,
        MaximumLights = 23,
        MaximumShadowLights = 6,
        MaximumParticleEmitters = 12,
        MaximumVisibleParticles = 180,
        MaximumActiveSounds = 16,
        MaximumAmbientBeds = 2,
        MaximumPathRecomputesPerSecond = 18,
    },

    GetWaveBudget = getWaveBudget,
    GetStorageCapacity = getStorageCapacity,
    GetRifleDamage = getRifleDamage,
    GetTreeDamage = getTreeDamage,
    IsIntegerInRange = isIntegerInRange,
}

return deepFreeze(Config)
