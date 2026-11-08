--!strict

local Config = require(script.Parent.Config)
local Definitions = require(script.Parent.Definitions)
local WorldManifest = require(script.Parent.WorldManifest)

export type ResultCode =
    "OK"
    | "INVALID_PAYLOAD"
    | "UNKNOWN_REQUEST"
    | "RATE_LIMITED"
    | "REPLAYED"
    | "PROFILE_NOT_READY"
    | "PROFILE_LOCKED"
    | "PROFILE_LOAD_FAILED"
    | "PROFILE_VERSION_UNSUPPORTED"
    | "PROFILE_CONFLICT"
    | "SERVER_FULL"
    | "PLAYER_DEAD"
    | "NO_CHARACTER"
    | "INVALID_SLOT"
    | "NOT_EQUIPPED"
    | "COOLDOWN"
    | "NO_AMMO"
    | "INVALID_AIM"
    | "OUT_OF_RANGE"
    | "LINE_OF_SIGHT_BLOCKED"
    | "UNKNOWN_TARGET"
    | "TARGET_INACTIVE"
    | "INVENTORY_FULL"
    | "NOT_ENOUGH_ITEMS"
    | "NOT_ENOUGH_CREDITS"
    | "STORAGE_FULL"
    | "ALREADY_OWNED"
    | "REQUIRES_POWER"
    | "INVALID_TOKEN"
    | "TOKEN_EXPIRED"
    | "WRONG_INTERACTION"
    | "PLOT_OCCUPIED"
    | "PLOT_NOT_READY"
    | "NOT_PLOT_OWNER"
    | "PROCESSOR_BUSY"
    | "POWER_ALREADY_ACTIVE"
    | "KILL_REWARD_CAPPED"

export type ItemQuantities = {
    axe_basic: number,
    rifle_basic: number,
    ammo_rifle: number,
    wood: number,
    scrap: number,
    battery_cell: number,
    seed_wheat: number,
    crop_wheat: number,
    food_ration: number,
}

export type PlayerView = {
    ProfileRevision: number,
    Inventory: ItemQuantities,
    Storage: ItemQuantities,
    StorageUsed: number,
    StorageCapacity: number,
    Credits: number,
    Upgrades: {
        harvest: number,
        weapon: number,
        storage: number,
    },
    Onboarding: {
        Version: number,
        Step: Definitions.OnboardingStep,
        Completed: boolean,
    },
    Stats: {
        HighestDay: number,
        ZombiesDefeated: number,
        TreesHarvested: number,
    },
    Health: number,
    MaxHealth: number,
    EquippedSlot: number,
    Hotbar: {
        {
            Slot: number,
            ItemId: "axe_basic",
            Owned: boolean,
            Equipped: boolean,
        } | {
            Slot: number,
            ItemId: "rifle_basic",
            Owned: boolean,
            Equipped: boolean,
        }
    },
    SpawnProtectionEndsAt: number,
}

export type WaveView = {
    State: "Idle" | "Spawning" | "Active" | "Complete",
    Revision: number,
    Budget: number,
    Spawned: number,
    Alive: number,
    EligiblePlayers: number,
}

export type PowerView = {
    IsActive: boolean,
    Generation: number,
    EndsAt: number,
}

export type SessionView = {
    Day: number,
    Phase: Definitions.Phase,
    PhaseRevision: number,
    PhaseEndsAt: number,
    Wave: WaveView,
    Power: PowerView,
}

export type PlotView = {
    PlotId: WorldManifest.PlotId,
    State: "Empty" | "Growing" | "Mature",
    IsOwned: boolean,
    IsOwnedByYou: boolean,
    CropId: Definitions.CropId?,
    ReadyAt: number,
}

export type ProcessorJobView = {
    State: "Processing",
    RecipeId: "food_ration_wheat",
    CompletesAt: number,
}

export type WorldView = {
    Plots: { PlotView },
    ProcessorJob: ProcessorJobView?,
}

export type Snapshot = {
    Protocol: number,
    ViewRevision: number,
    ServerTime: number,
    Player: PlayerView,
    Session: SessionView,
    World: WorldView,
}

export type GetSnapshotResponse =
    { Success: true, Code: "OK", Snapshot: Snapshot }
    | {
        Success: false,
        Code: "PROFILE_NOT_READY" | "PROFILE_LOAD_FAILED" | "RATE_LIMITED",
        RetryAfter: number,
    }

export type ToolIntent =
    { RequestId: string, Kind: "Equip", Slot: number }
    | { RequestId: string, Kind: "Primary", AimDirection: Vector3 }

export type UseItemIntent = {
    RequestId: string,
    Kind: "UseItem",
    ItemId: "food_ration",
}

export type InteractionIntent =
    { RequestId: string, Kind: "FarmPlant", InteractionId: string, Token: string, CropId: "wheat" }
    | { RequestId: string, Kind: "FarmHarvest", InteractionId: string, Token: string }
    | { RequestId: string, Kind: "ProcessorStart", InteractionId: string, Token: string, RecipeId: "food_ration_wheat" }
    | { RequestId: string, Kind: "ShopBuy", InteractionId: string, Token: string, OfferId: Definitions.OfferId, Count: number }
    | { RequestId: string, Kind: "StorageTransfer", InteractionId: string, Token: string, Direction: "deposit" | "withdraw", ItemId: Definitions.ItemId, Count: number }
    | { RequestId: string, Kind: "PowerActivate", InteractionId: string, Token: string }
    | { RequestId: string, Kind: "ScrapExchange", InteractionId: string, Token: string, Count: number }
    | { RequestId: string, Kind: "UpgradeBuy", InteractionId: string, Token: string, UpgradeId: Definitions.UpgradeId }

-- Closing a panel never mutates a gameplay domain. The server only clears the
-- matching session owned by this player, so a delayed close cannot revoke a
-- newer session token.
export type InteractionCloseIntent = {
    Token: string,
}

export type InteractionView =
    { Kind: "farm_plot", Plot: PlotView, SeedQuantity: number }
    | { Kind: "food_processor", IsPowered: boolean, CropQuantity: number, Job: ProcessorJobView? }
    | {
        Kind: "shop",
        Credits: number,
        Offers: { { OfferId: Definitions.OfferId, BundleCount: number, CreditCost: number } },
    }
    | {
        Kind: "storage",
        Inventory: ItemQuantities,
        Storage: ItemQuantities,
        StorageUsed: number,
        StorageCapacity: number,
    }
    | { Kind: "power", IsActive: boolean, EndsAt: number, BatteryQuantity: number }
    | { Kind: "scrap_exchange", ScrapQuantity: number, Credits: number, CreditsPerScrap: number }
    | {
        Kind: "upgrade",
        UpgradeId: Definitions.UpgradeId,
        Tier: number,
        CreditCost: number,
        Credits: number,
        IsPowered: boolean,
    }

export type InteractionOpened = {
    InteractionId: string,
    InteractionKind: Definitions.InteractionKind,
    Token: string,
    ExpiresAt: number,
    Actions: { Definitions.InteractionAction },
    View: InteractionView,
}

export type ActionPayload =
    { Kind: "Equip", EquippedSlot: number }
    | { Kind: "Primary", HitKind: "None" | "Tree" | "Zombie", TargetId: string?, TargetHealth: number?, AmmoRemaining: number }
    | { Kind: "UseItem", ItemId: "food_ration", Quantity: number, Health: number, MaxHealth: number }
    | { Kind: "FarmPlant", PlotId: string, State: "Growing", ReadyAt: number }
    | { Kind: "FarmHarvest", PlotId: string, State: "Empty", CropGranted: number, SeedGranted: number }
    | { Kind: "ProcessorStart", RecipeId: "food_ration_wheat", CompletesAt: number }
    | { Kind: "ShopBuy", OfferId: Definitions.OfferId, Count: number, Credits: number, GrantedItemId: Definitions.ItemId, GrantedQuantity: number }
    | { Kind: "StorageTransfer", Direction: "deposit" | "withdraw", ItemId: Definitions.ItemId, Count: number, StorageUsed: number, StorageCapacity: number }
    | { Kind: "PowerActivate", EndsAt: number, BatteryQuantity: number }
    | { Kind: "ScrapExchange", Count: number, Credits: number, ScrapQuantity: number }
    | { Kind: "UpgradeBuy", UpgradeId: Definitions.UpgradeId, Tier: number, Credits: number }

export type ActionResult = {
    RequestId: string,
    Success: boolean,
    Code: ResultCode,
    Revision: number,
    Payload: ActionPayload?,
}

export type StateDelta = {
    Protocol: number,
    BaseRevision: number,
    Revision: number,
    ServerTime: number,
    Domain: "Player" | "Session" | "World",
    Value: PlayerView | SessionView | WorldView,
}

local ITEM_KEYS = {
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

local ResultCodes: { ResultCode } = {
    "OK",
    "INVALID_PAYLOAD",
    "UNKNOWN_REQUEST",
    "RATE_LIMITED",
    "REPLAYED",
    "PROFILE_NOT_READY",
    "PROFILE_LOCKED",
    "PROFILE_LOAD_FAILED",
    "PROFILE_VERSION_UNSUPPORTED",
    "PROFILE_CONFLICT",
    "SERVER_FULL",
    "PLAYER_DEAD",
    "NO_CHARACTER",
    "INVALID_SLOT",
    "NOT_EQUIPPED",
    "COOLDOWN",
    "NO_AMMO",
    "INVALID_AIM",
    "OUT_OF_RANGE",
    "LINE_OF_SIGHT_BLOCKED",
    "UNKNOWN_TARGET",
    "TARGET_INACTIVE",
    "INVENTORY_FULL",
    "NOT_ENOUGH_ITEMS",
    "NOT_ENOUGH_CREDITS",
    "STORAGE_FULL",
    "ALREADY_OWNED",
    "REQUIRES_POWER",
    "INVALID_TOKEN",
    "TOKEN_EXPIRED",
    "WRONG_INTERACTION",
    "PLOT_OCCUPIED",
    "PLOT_NOT_READY",
    "NOT_PLOT_OWNER",
    "PROCESSOR_BUSY",
    "POWER_ALREADY_ACTIVE",
    "KILL_REWARD_CAPPED",
}

local ResultCodeSet: { [string]: boolean } = {}
for _, code in ipairs(ResultCodes) do
    ResultCodeSet[code] = true
end

local RemoteDefinitions = {
    GetSnapshot = { ClassName = "RemoteFunction", Direction = "ClientToServer", ArgumentCount = 0 },
    StateDelta = { ClassName = "RemoteEvent", Direction = "ServerToClient" },
    ActionResult = { ClassName = "RemoteEvent", Direction = "ServerToClient" },
    InteractionOpened = { ClassName = "RemoteEvent", Direction = "ServerToClient" },
    ToolIntent = { ClassName = "RemoteEvent", Direction = "ClientToServer" },
    InteractionIntent = { ClassName = "RemoteEvent", Direction = "ClientToServer" },
    InteractionCloseIntent = { ClassName = "RemoteEvent", Direction = "ClientToServer" },
    UseItemIntent = { ClassName = "RemoteEvent", Direction = "ClientToServer" },
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

local function deepCopyInternal(value: any, seen: { [any]: any }): any
    if type(value) ~= "table" then
        return value
    end

    local prior = seen[value]
    if prior ~= nil then
        return prior
    end

    local copy = {}
    seen[value] = copy
    for key, child in pairs(value) do
        copy[deepCopyInternal(key, seen)] = deepCopyInternal(child, seen)
    end
    return copy
end

local function deepCopy<T>(value: T): T
    return deepCopyInternal(value, {}) :: T
end

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

local function contains(values: { string }, sought: unknown): boolean
    for _, value in ipairs(values) do
        if value == sought then
            return true
        end
    end
    return false
end

local function hasExactShape(value: { [any]: any }, required: { string }, optional: { string }?): boolean
    for key in pairs(value) do
        if type(key) ~= "string" or (not contains(required, key) and (optional == nil or not contains(optional, key))) then
            return false
        end
    end
    for _, key in ipairs(required) do
        if value[key] == nil then
            return false
        end
    end
    return true
end

local function isExactArray(value: unknown, length: number): boolean
    local array = asPlainTable(value)
    if array == nil then
        return false
    end
    for key in pairs(array) do
        if type(key) ~= "number" or math.floor(key) ~= key or key < 1 or key > length then
            return false
        end
    end
    for index = 1, length do
        if array[index] == nil then
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

local function isNonnegativeTimestamp(value: unknown): boolean
    return isFiniteNumber(value) and (value :: number) >= 0
end

local function isInteger(value: unknown, minimum: number, maximum: number): boolean
    return type(value) == "number" and Config.IsIntegerInRange(value, minimum, maximum)
end

local function isPrintableAscii(value: unknown, minimumLength: number, maximumLength: number): boolean
    if type(value) ~= "string" or #value < minimumLength or #value > maximumLength then
        return false
    end
    for index = 1, #value do
        local byte = string.byte(value, index)
        if byte < 32 or byte > 126 then
            return false
        end
    end
    return true
end

local function isRequestId(value: unknown): boolean
    return type(value) == "string"
        and #value >= Config.Network.RequestIdMinimumLength
        and #value <= Config.Network.RequestIdMaximumLength
        and string.match(value, "^[A-Za-z0-9_-]+$") ~= nil
end

local function isCanonicalId(value: unknown): boolean
    return isPrintableAscii(
        value,
        Config.Network.CanonicalIdMinimumLength,
        Config.Network.CanonicalIdMaximumLength
    )
end

local function isToken(value: unknown): boolean
    return type(value) == "string"
        and #value == Config.Network.StationTokenLength
        and string.match(value, "^[0-9a-f]+$") ~= nil
end

local function isAimDirection(value: unknown): boolean
    if typeof(value) ~= "Vector3" then
        return false
    end
    local vector = value :: Vector3
    if not isFiniteNumber(vector.X) or not isFiniteNumber(vector.Y) or not isFiniteNumber(vector.Z) then
        return false
    end
    return vector.Magnitude >= Config.Network.AimMagnitudeMinimum
        and vector.Magnitude <= Config.Network.AimMagnitudeMaximum
end

local function validateItemQuantities(value: unknown, isStorage: boolean): boolean
    local quantities = asPlainTable(value)
    if quantities == nil or not hasExactShape(quantities, ITEM_KEYS, nil) then
        return false
    end
    for _, itemId in ipairs(ITEM_KEYS) do
        local definition = Definitions.Items[itemId]
        local quantity = quantities[itemId]
        if not isInteger(quantity, 0, definition.StackCap) then
            return false
        end
        if isStorage and not definition.StorageAllowed and quantity ~= 0 then
            return false
        end
    end
    return true
end

local function validateUpgrades(value: unknown): boolean
    local upgrades = asPlainTable(value)
    if upgrades == nil or not hasExactShape(upgrades, { "harvest", "weapon", "storage" }, nil) then
        return false
    end
    return isInteger(upgrades.harvest, 0, 1)
        and isInteger(upgrades.weapon, 0, 1)
        and isInteger(upgrades.storage, 0, 1)
end

local function validateOnboarding(value: unknown): boolean
    local onboarding = asPlainTable(value)
    if onboarding == nil or not hasExactShape(onboarding, { "Version", "Step", "Completed" }, nil) then
        return false
    end
    return onboarding.Version == 1
        and Definitions.IsOnboardingStep(onboarding.Step)
        and type(onboarding.Completed) == "boolean"
        and onboarding.Completed == (onboarding.Step == "onboarding_complete")
end

local function validateStats(value: unknown): boolean
    local stats = asPlainTable(value)
    if stats == nil or not hasExactShape(stats, { "HighestDay", "ZombiesDefeated", "TreesHarvested" }, nil) then
        return false
    end
    return isInteger(stats.HighestDay, 0, Config.Profile.RevisionMaximum)
        and isInteger(stats.ZombiesDefeated, 0, Config.Profile.RevisionMaximum)
        and isInteger(stats.TreesHarvested, 0, Config.Profile.RevisionMaximum)
end

local function storageUsed(storage: { [any]: any }): number
    local used = 0
    for _, itemId in ipairs(ITEM_KEYS) do
        used += storage[itemId]
    end
    return used
end

local function validatePlayerView(value: unknown): boolean
    local view = asPlainTable(value)
    if view == nil or not hasExactShape(view, {
        "ProfileRevision",
        "Inventory",
        "Storage",
        "StorageUsed",
        "StorageCapacity",
        "Credits",
        "Upgrades",
        "Onboarding",
        "Stats",
        "Health",
        "MaxHealth",
        "EquippedSlot",
        "Hotbar",
        "SpawnProtectionEndsAt",
    }, nil) then
        return false
    end
    if not isInteger(view.ProfileRevision, 0, Config.Profile.RevisionMaximum)
        or not validateItemQuantities(view.Inventory, false)
        or not validateItemQuantities(view.Storage, true)
        or not validateUpgrades(view.Upgrades)
        or not validateOnboarding(view.Onboarding)
        or not validateStats(view.Stats)
        or not isInteger(view.Credits, 0, Config.Profile.CreditsMaximum)
        or not isFiniteNumber(view.MaxHealth)
        or view.MaxHealth <= 0
        or not isFiniteNumber(view.Health)
        or view.Health < 0
        or view.Health > view.MaxHealth
        or (view.EquippedSlot ~= 0 and view.EquippedSlot ~= 1 and view.EquippedSlot ~= 2)
        or not isNonnegativeTimestamp(view.SpawnProtectionEndsAt)
    then
        return false
    end

    local upgrades = view.Upgrades :: { [any]: any }
    local storage = view.Storage :: { [any]: any }
    local expectedCapacity = Config.GetStorageCapacity(upgrades.storage)
    if view.StorageCapacity ~= expectedCapacity
        or not isInteger(view.StorageUsed, 0, expectedCapacity)
        or view.StorageUsed ~= storageUsed(storage)
    then
        return false
    end

    if not isExactArray(view.Hotbar, 2) then
        return false
    end
    local inventory = view.Inventory :: { [any]: any }
    local hotbar = view.Hotbar :: { [any]: any }
    for slot = 1, 2 do
        local entry = asPlainTable(hotbar[slot])
        local expectedItemId = if slot == 1 then "axe_basic" else "rifle_basic"
        if entry == nil
            or not hasExactShape(entry, { "Slot", "ItemId", "Owned", "Equipped" }, nil)
            or entry.Slot ~= slot
            or entry.ItemId ~= expectedItemId
            or type(entry.Owned) ~= "boolean"
            or type(entry.Equipped) ~= "boolean"
            or entry.Owned ~= (inventory[expectedItemId] > 0)
            or entry.Equipped ~= (view.EquippedSlot == slot)
        then
            return false
        end
    end

    return true
end

local function validateWaveView(value: unknown): boolean
    local wave = asPlainTable(value)
    if wave == nil or not hasExactShape(wave, { "State", "Revision", "Budget", "Spawned", "Alive", "EligiblePlayers" }, nil) then
        return false
    end
    if not contains({ "Idle", "Spawning", "Active", "Complete" }, wave.State)
        or not isInteger(wave.Revision, 0, Config.Profile.RevisionMaximum)
        or not isInteger(wave.Budget, 0, Config.Gameplay.Wave.ActiveCap)
        or not isInteger(wave.Spawned, 0, wave.Budget)
        or not isInteger(wave.Alive, 0, wave.Spawned)
        or not isInteger(wave.EligiblePlayers, 0, Config.Server.MaxActivePlayers)
    then
        return false
    end
    return true
end

local function validatePowerView(value: unknown): boolean
    local power = asPlainTable(value)
    return power ~= nil
        and hasExactShape(power, { "IsActive", "Generation", "EndsAt" }, nil)
        and type(power.IsActive) == "boolean"
        and isInteger(power.Generation, 0, Config.Profile.RevisionMaximum)
        and isNonnegativeTimestamp(power.EndsAt)
end

local function validateSessionView(value: unknown): boolean
    local view = asPlainTable(value)
    return view ~= nil
        and hasExactShape(view, { "Day", "Phase", "PhaseRevision", "PhaseEndsAt", "Wave", "Power" }, nil)
        and isInteger(view.Day, 1, Config.Profile.RevisionMaximum)
        and Definitions.IsPhase(view.Phase)
        and isInteger(view.PhaseRevision, 0, Config.Profile.RevisionMaximum)
        and isNonnegativeTimestamp(view.PhaseEndsAt)
        and validateWaveView(view.Wave)
        and validatePowerView(view.Power)
end

local function validatePlotView(value: unknown): boolean
    local plot = asPlainTable(value)
    if plot == nil
        or not hasExactShape(plot, { "PlotId", "State", "IsOwned", "IsOwnedByYou", "ReadyAt" }, { "CropId" })
        or not WorldManifest.IsPlotId(plot.PlotId)
        or not contains({ "Empty", "Growing", "Mature" }, plot.State)
        or type(plot.IsOwned) ~= "boolean"
        or type(plot.IsOwnedByYou) ~= "boolean"
        or (plot.IsOwnedByYou and not plot.IsOwned)
        or not isNonnegativeTimestamp(plot.ReadyAt)
    then
        return false
    end
    if plot.State == "Empty" then
        return plot.CropId == nil
    end
    return plot.CropId == "wheat" and plot.IsOwned
end

local function validateProcessorJob(value: unknown): boolean
    local job = asPlainTable(value)
    return job ~= nil
        and hasExactShape(job, { "State", "RecipeId", "CompletesAt" }, nil)
        and job.State == "Processing"
        and job.RecipeId == "food_ration_wheat"
        and isNonnegativeTimestamp(job.CompletesAt)
end

local function validateWorldView(value: unknown): boolean
    local view = asPlainTable(value)
    if view == nil or not hasExactShape(view, { "Plots" }, { "ProcessorJob" }) or not isExactArray(view.Plots, 12) then
        return false
    end
    local plots = view.Plots :: { [any]: any }
    for index, expected in ipairs(WorldManifest.Plots) do
        if not validatePlotView(plots[index]) or plots[index].PlotId ~= expected.Id then
            return false
        end
    end
    return view.ProcessorJob == nil or validateProcessorJob(view.ProcessorJob)
end

local function validateSnapshot(value: unknown): boolean
    local snapshot = asPlainTable(value)
    return snapshot ~= nil
        and hasExactShape(snapshot, { "Protocol", "ViewRevision", "ServerTime", "Player", "Session", "World" }, nil)
        and snapshot.Protocol == Config.ProtocolVersion
        and isInteger(snapshot.ViewRevision, 0, Config.Profile.RevisionMaximum)
        and isNonnegativeTimestamp(snapshot.ServerTime)
        and validatePlayerView(snapshot.Player)
        and validateSessionView(snapshot.Session)
        and validateWorldView(snapshot.World)
end

local function validateToolIntent(value: unknown): boolean
    local intent = asPlainTable(value)
    if intent == nil or not isRequestId(intent.RequestId) then
        return false
    end
    if intent.Kind == "Equip" then
        return hasExactShape(intent, { "RequestId", "Kind", "Slot" }, nil)
            and (intent.Slot == 1 or intent.Slot == 2)
    elseif intent.Kind == "Primary" then
        return hasExactShape(intent, { "RequestId", "Kind", "AimDirection" }, nil)
            and isAimDirection(intent.AimDirection)
    end
    return false
end

local function validateUseItemIntent(value: unknown): boolean
    local intent = asPlainTable(value)
    return intent ~= nil
        and hasExactShape(intent, { "RequestId", "Kind", "ItemId" }, nil)
        and isRequestId(intent.RequestId)
        and intent.Kind == "UseItem"
        and intent.ItemId == "food_ration"
end

local function interactionBaseIsValid(intent: { [any]: any }, expectedKind: Definitions.InteractionKind): boolean
    return isRequestId(intent.RequestId)
        and isCanonicalId(intent.InteractionId)
        and WorldManifest.GetInteractionKind(intent.InteractionId) == expectedKind
        and isToken(intent.Token)
end

local function validateInteractionIntent(value: unknown): boolean
    local intent = asPlainTable(value)
    if intent == nil or type(intent.Kind) ~= "string" then
        return false
    end

    if intent.Kind == "FarmPlant" then
        return hasExactShape(intent, { "RequestId", "Kind", "InteractionId", "Token", "CropId" }, nil)
            and interactionBaseIsValid(intent, "farm_plot")
            and intent.CropId == "wheat"
    elseif intent.Kind == "FarmHarvest" then
        return hasExactShape(intent, { "RequestId", "Kind", "InteractionId", "Token" }, nil)
            and interactionBaseIsValid(intent, "farm_plot")
    elseif intent.Kind == "ProcessorStart" then
        return hasExactShape(intent, { "RequestId", "Kind", "InteractionId", "Token", "RecipeId" }, nil)
            and interactionBaseIsValid(intent, "food_processor")
            and intent.RecipeId == "food_ration_wheat"
    elseif intent.Kind == "ShopBuy" then
        return hasExactShape(intent, { "RequestId", "Kind", "InteractionId", "Token", "OfferId", "Count" }, nil)
            and interactionBaseIsValid(intent, "shop")
            and Definitions.IsOfferId(intent.OfferId)
            and isInteger(intent.Count, Config.Gameplay.Economy.ShopBundleCountMinimum, Config.Gameplay.Economy.ShopBundleCountMaximum)
    elseif intent.Kind == "StorageTransfer" then
        return hasExactShape(intent, { "RequestId", "Kind", "InteractionId", "Token", "Direction", "ItemId", "Count" }, nil)
            and interactionBaseIsValid(intent, "storage")
            and (intent.Direction == "deposit" or intent.Direction == "withdraw")
            and Definitions.IsItemId(intent.ItemId)
            and isInteger(intent.Count, Config.Network.DefaultCountMinimum, Config.Network.DefaultCountMaximum)
    elseif intent.Kind == "PowerActivate" then
        return hasExactShape(intent, { "RequestId", "Kind", "InteractionId", "Token" }, nil)
            and interactionBaseIsValid(intent, "power")
    elseif intent.Kind == "ScrapExchange" then
        return hasExactShape(intent, { "RequestId", "Kind", "InteractionId", "Token", "Count" }, nil)
            and interactionBaseIsValid(intent, "scrap_exchange")
            and isInteger(intent.Count, Config.Gameplay.Economy.ScrapExchangeMinimum, Config.Gameplay.Economy.ScrapExchangeMaximum)
    elseif intent.Kind == "UpgradeBuy" then
        return hasExactShape(intent, { "RequestId", "Kind", "InteractionId", "Token", "UpgradeId" }, nil)
            and interactionBaseIsValid(intent, "upgrade")
            and Definitions.IsUpgradeId(intent.UpgradeId)
            and WorldManifest.GetUpgradeId(intent.InteractionId) == intent.UpgradeId
    end
    return false
end

local function validateInteractionCloseIntent(value: unknown): boolean
    local intent = asPlainTable(value)
    return intent ~= nil
        and hasExactShape(intent, { "Token" }, nil)
        and isToken(intent.Token)
end

local function validateOffers(value: unknown): boolean
    if not isExactArray(value, 4) then
        return false
    end
    local offers = value :: { [any]: any }
    for index, offerId in ipairs(Definitions.OfferIds) do
        local offer = asPlainTable(offers[index])
        local definition = Definitions.Offers[offerId]
        if offer == nil
            or not hasExactShape(offer, { "OfferId", "BundleCount", "CreditCost" }, nil)
            or offer.OfferId ~= offerId
            or offer.BundleCount ~= definition.BundleCount
            or offer.CreditCost ~= definition.CreditCost
        then
            return false
        end
    end
    return true
end

local function validateInteractionView(value: unknown): boolean
    local view = asPlainTable(value)
    if view == nil or type(view.Kind) ~= "string" then
        return false
    end
    if view.Kind == "farm_plot" then
        return hasExactShape(view, { "Kind", "Plot", "SeedQuantity" }, nil)
            and validatePlotView(view.Plot)
            and isInteger(view.SeedQuantity, 0, Definitions.Items.seed_wheat.StackCap)
    elseif view.Kind == "food_processor" then
        return hasExactShape(view, { "Kind", "IsPowered", "CropQuantity" }, { "Job" })
            and type(view.IsPowered) == "boolean"
            and isInteger(view.CropQuantity, 0, Definitions.Items.crop_wheat.StackCap)
            and (view.Job == nil or validateProcessorJob(view.Job))
    elseif view.Kind == "shop" then
        return hasExactShape(view, { "Kind", "Credits", "Offers" }, nil)
            and isInteger(view.Credits, 0, Config.Profile.CreditsMaximum)
            and validateOffers(view.Offers)
    elseif view.Kind == "storage" then
        if not hasExactShape(view, { "Kind", "Inventory", "Storage", "StorageUsed", "StorageCapacity" }, nil)
            or not validateItemQuantities(view.Inventory, false)
            or not validateItemQuantities(view.Storage, true)
            or (view.StorageCapacity ~= 80 and view.StorageCapacity ~= 120)
            or not isInteger(view.StorageUsed, 0, view.StorageCapacity)
        then
            return false
        end
        return view.StorageUsed == storageUsed(view.Storage)
    elseif view.Kind == "power" then
        return hasExactShape(view, { "Kind", "IsActive", "EndsAt", "BatteryQuantity" }, nil)
            and type(view.IsActive) == "boolean"
            and isNonnegativeTimestamp(view.EndsAt)
            and isInteger(view.BatteryQuantity, 0, Definitions.Items.battery_cell.StackCap)
    elseif view.Kind == "scrap_exchange" then
        return hasExactShape(view, { "Kind", "ScrapQuantity", "Credits", "CreditsPerScrap" }, nil)
            and isInteger(view.ScrapQuantity, 0, Definitions.Items.scrap.StackCap)
            and isInteger(view.Credits, 0, Config.Profile.CreditsMaximum)
            and view.CreditsPerScrap == Config.Gameplay.Economy.ScrapCreditsEach
    elseif view.Kind == "upgrade" then
        if not hasExactShape(view, { "Kind", "UpgradeId", "Tier", "CreditCost", "Credits", "IsPowered" }, nil)
            or not Definitions.IsUpgradeId(view.UpgradeId)
            or not isInteger(view.Tier, 0, 1)
            or not isInteger(view.Credits, 0, Config.Profile.CreditsMaximum)
            or type(view.IsPowered) ~= "boolean"
        then
            return false
        end
        return view.CreditCost == Definitions.Upgrades[view.UpgradeId].CreditCost
    end
    return false
end

local ACTIONS_BY_KIND: { [string]: { string } } = {
    farm_plot = { "FarmHarvest", "FarmPlant" },
    food_processor = { "ProcessorStart" },
    shop = { "ShopBuy" },
    storage = { "StorageTransfer" },
    power = { "PowerActivate" },
    scrap_exchange = { "ScrapExchange" },
    upgrade = { "UpgradeBuy" },
}

local function validateActions(value: unknown, interactionKind: string): boolean
	local actions = asPlainTable(value)
	local expected = ACTIONS_BY_KIND[interactionKind]
	if actions == nil or expected == nil then
		return false
	end
    local length = 0
    for key in pairs(actions) do
        if type(key) ~= "number" or math.floor(key) ~= key or key < 1 then
            return false
        end
        length = math.max(length, key)
    end
	if length ~= #expected then
		return false
	end
	for index = 1, length do
		local action = actions[index]
		if action == nil
			or action ~= expected[index]
		then
			return false
        end
    end
    return true
end

local function validateInteractionOpened(value: unknown): boolean
    local opened = asPlainTable(value)
    if opened == nil
        or not hasExactShape(opened, { "InteractionId", "InteractionKind", "Token", "ExpiresAt", "Actions", "View" }, nil)
        or not isCanonicalId(opened.InteractionId)
        or WorldManifest.GetInteractionKind(opened.InteractionId) ~= opened.InteractionKind
        or not isToken(opened.Token)
        or not isNonnegativeTimestamp(opened.ExpiresAt)
        or not validateActions(opened.Actions, opened.InteractionKind)
        or not validateInteractionView(opened.View)
        or opened.View.Kind ~= opened.InteractionKind
    then
        return false
    end
    if opened.InteractionKind == "farm_plot" and opened.View.Plot.PlotId ~= opened.InteractionId then
        return false
    end
    if opened.InteractionKind == "upgrade" then
        return opened.View.UpgradeId == WorldManifest.GetUpgradeId(opened.InteractionId)
    end
    return true
end

local function validateActionPayload(value: unknown): boolean
    local payload = asPlainTable(value)
    if payload == nil or type(payload.Kind) ~= "string" then
        return false
    end
    if payload.Kind == "Equip" then
        return hasExactShape(payload, { "Kind", "EquippedSlot" }, nil)
            and (payload.EquippedSlot == 1 or payload.EquippedSlot == 2)
    elseif payload.Kind == "Primary" then
        if not hasExactShape(payload, { "Kind", "HitKind", "AmmoRemaining" }, { "TargetId", "TargetHealth" })
            or not contains({ "None", "Tree", "Zombie" }, payload.HitKind)
            or not isInteger(payload.AmmoRemaining, 0, Definitions.Items.ammo_rifle.StackCap)
        then
            return false
        end
        if payload.HitKind == "None" then
            return payload.TargetId == nil and payload.TargetHealth == nil
        end
        return isCanonicalId(payload.TargetId)
            and isFiniteNumber(payload.TargetHealth)
            and payload.TargetHealth >= 0
    elseif payload.Kind == "UseItem" then
        return hasExactShape(payload, { "Kind", "ItemId", "Quantity", "Health", "MaxHealth" }, nil)
            and payload.ItemId == "food_ration"
            and isInteger(payload.Quantity, 0, Definitions.Items.food_ration.StackCap)
            and isFiniteNumber(payload.MaxHealth)
            and payload.MaxHealth > 0
            and isFiniteNumber(payload.Health)
            and payload.Health >= 0
            and payload.Health <= payload.MaxHealth
    elseif payload.Kind == "FarmPlant" then
        return hasExactShape(payload, { "Kind", "PlotId", "State", "ReadyAt" }, nil)
            and WorldManifest.IsPlotId(payload.PlotId)
            and payload.State == "Growing"
            and isNonnegativeTimestamp(payload.ReadyAt)
    elseif payload.Kind == "FarmHarvest" then
        return hasExactShape(payload, { "Kind", "PlotId", "State", "CropGranted", "SeedGranted" }, nil)
            and WorldManifest.IsPlotId(payload.PlotId)
            and payload.State == "Empty"
            and payload.CropGranted == Config.Gameplay.Wheat.CropReward
            and payload.SeedGranted == Config.Gameplay.Wheat.SeedReward
    elseif payload.Kind == "ProcessorStart" then
        return hasExactShape(payload, { "Kind", "RecipeId", "CompletesAt" }, nil)
            and payload.RecipeId == "food_ration_wheat"
            and isNonnegativeTimestamp(payload.CompletesAt)
    elseif payload.Kind == "ShopBuy" then
        if not hasExactShape(payload, { "Kind", "OfferId", "Count", "Credits", "GrantedItemId", "GrantedQuantity" }, nil)
            or not Definitions.IsOfferId(payload.OfferId)
            or not isInteger(payload.Count, 1, 5)
            or not isInteger(payload.Credits, 0, Config.Profile.CreditsMaximum)
        then
            return false
        end
        local offer = Definitions.Offers[payload.OfferId]
        return payload.GrantedItemId == offer.ItemId
            and payload.GrantedQuantity == offer.BundleCount * payload.Count
    elseif payload.Kind == "StorageTransfer" then
        return hasExactShape(payload, { "Kind", "Direction", "ItemId", "Count", "StorageUsed", "StorageCapacity" }, nil)
            and (payload.Direction == "deposit" or payload.Direction == "withdraw")
            and Definitions.IsItemId(payload.ItemId)
            and isInteger(payload.Count, 1, 50)
            and (payload.StorageCapacity == 80 or payload.StorageCapacity == 120)
            and isInteger(payload.StorageUsed, 0, payload.StorageCapacity)
    elseif payload.Kind == "PowerActivate" then
        return hasExactShape(payload, { "Kind", "EndsAt", "BatteryQuantity" }, nil)
            and isNonnegativeTimestamp(payload.EndsAt)
            and isInteger(payload.BatteryQuantity, 0, Definitions.Items.battery_cell.StackCap)
    elseif payload.Kind == "ScrapExchange" then
        return hasExactShape(payload, { "Kind", "Count", "Credits", "ScrapQuantity" }, nil)
            and isInteger(payload.Count, 1, 20)
            and isInteger(payload.Credits, 0, Config.Profile.CreditsMaximum)
            and isInteger(payload.ScrapQuantity, 0, Definitions.Items.scrap.StackCap)
    elseif payload.Kind == "UpgradeBuy" then
        return hasExactShape(payload, { "Kind", "UpgradeId", "Tier", "Credits" }, nil)
            and Definitions.IsUpgradeId(payload.UpgradeId)
            and payload.Tier == 1
            and isInteger(payload.Credits, 0, Config.Profile.CreditsMaximum)
    end
    return false
end

local function validateActionResult(value: unknown): boolean
    local result = asPlainTable(value)
    if result == nil
        or not hasExactShape(result, { "RequestId", "Success", "Code", "Revision" }, { "Payload" })
        or not isRequestId(result.RequestId)
        or type(result.Success) ~= "boolean"
        or ResultCodeSet[result.Code] ~= true
        or not isInteger(result.Revision, 0, Config.Profile.RevisionMaximum)
    then
        return false
    end
    if result.Success then
        return (result.Code == "OK" or result.Code == "KILL_REWARD_CAPPED")
            and result.Payload ~= nil
            and validateActionPayload(result.Payload)
    end
    return result.Code ~= "OK" and result.Code ~= "KILL_REWARD_CAPPED" and result.Payload == nil
end

local function validateGetSnapshotResponse(value: unknown): boolean
    local response = asPlainTable(value)
    if response == nil or type(response.Success) ~= "boolean" then
        return false
    end
    if response.Success then
        return hasExactShape(response, { "Success", "Code", "Snapshot" }, nil)
            and response.Code == "OK"
            and validateSnapshot(response.Snapshot)
    end
    return hasExactShape(response, { "Success", "Code", "RetryAfter" }, nil)
        and contains({ "PROFILE_NOT_READY", "PROFILE_LOAD_FAILED", "RATE_LIMITED" }, response.Code)
        and isFiniteNumber(response.RetryAfter)
        and response.RetryAfter >= Config.Network.SnapshotRetryMinimumSeconds
        and response.RetryAfter <= Config.Network.SnapshotRetryMaximumSeconds
end

local function validateStateDelta(value: unknown): boolean
    local delta = asPlainTable(value)
    if delta == nil
        or not hasExactShape(delta, { "Protocol", "BaseRevision", "Revision", "ServerTime", "Domain", "Value" }, nil)
        or delta.Protocol ~= Config.ProtocolVersion
        or not isInteger(delta.BaseRevision, 0, Config.Profile.RevisionMaximum - 1)
        or delta.Revision ~= delta.BaseRevision + 1
        or not isNonnegativeTimestamp(delta.ServerTime)
    then
        return false
    end
    if delta.Domain == "Player" then
        return validatePlayerView(delta.Value)
    elseif delta.Domain == "Session" then
        return validateSessionView(delta.Value)
    elseif delta.Domain == "World" then
        return validateWorldView(delta.Value)
    end
    return false
end

local function validateRemoteContainer(container: Instance): (boolean, string?)
    if not container:IsA("Folder") or container.Name ~= "Remotes" then
        return false, "remote container must be ReplicatedStorage.Remotes Folder"
    end

    local children = container:GetChildren()
    local expectedCount = 0
    for remoteName, definition in pairs(RemoteDefinitions) do
        expectedCount += 1
        local child = container:FindFirstChild(remoteName)
        if child == nil or child.ClassName ~= definition.ClassName then
            return false, string.format("Remotes.%s must be %s", remoteName, definition.ClassName)
        end
    end
    if #children ~= expectedCount then
        return false, "Remotes contains missing or extra instances"
    end
    return true, nil
end

local function validationResult(ok: boolean, contractName: string): (boolean, string?)
    if ok then
        return true, nil
    end
    return false, contractName .. " violates the frozen network contract"
end

local NetTypes = {
    ProtocolVersion = Config.ProtocolVersion,
    ResultCodes = ResultCodes,
    ResultCodeSet = ResultCodeSet,
    RemoteDefinitions = RemoteDefinitions,

    IsRequestId = isRequestId,
    IsCanonicalId = isCanonicalId,
    IsStationToken = isToken,
    IsAimDirection = isAimDirection,
    IsResultCode = function(value: unknown): boolean
        return type(value) == "string" and ResultCodeSet[value] == true
    end,
    ValidateGetSnapshotArguments = function(argumentCount: number): (boolean, string?)
        return validationResult(argumentCount == 0, "GetSnapshot arguments")
    end,
    ValidateToolIntent = function(value: unknown): (boolean, string?)
        return validationResult(validateToolIntent(value), "ToolIntent")
    end,
    ValidateInteractionIntent = function(value: unknown): (boolean, string?)
        return validationResult(validateInteractionIntent(value), "InteractionIntent")
    end,
    ValidateInteractionCloseIntent = function(value: unknown): (boolean, string?)
        return validationResult(validateInteractionCloseIntent(value), "InteractionCloseIntent")
    end,
    ValidateUseItemIntent = function(value: unknown): (boolean, string?)
        return validationResult(validateUseItemIntent(value), "UseItemIntent")
    end,
    ValidatePlayerView = function(value: unknown): (boolean, string?)
        return validationResult(validatePlayerView(value), "PlayerView")
    end,
    ValidateSessionView = function(value: unknown): (boolean, string?)
        return validationResult(validateSessionView(value), "SessionView")
    end,
    ValidateWorldView = function(value: unknown): (boolean, string?)
        return validationResult(validateWorldView(value), "WorldView")
    end,
    ValidateSnapshot = function(value: unknown): (boolean, string?)
        return validationResult(validateSnapshot(value), "Snapshot")
    end,
    ValidateGetSnapshotResponse = function(value: unknown): (boolean, string?)
        return validationResult(validateGetSnapshotResponse(value), "GetSnapshotResponse")
    end,
    ValidateInteractionOpened = function(value: unknown): (boolean, string?)
        return validationResult(validateInteractionOpened(value), "InteractionOpened")
    end,
    ValidateActionResult = function(value: unknown): (boolean, string?)
        return validationResult(validateActionResult(value), "ActionResult")
    end,
    ValidateStateDelta = function(value: unknown): (boolean, string?)
        return validationResult(validateStateDelta(value), "StateDelta")
    end,
    ValidateRemoteContainer = validateRemoteContainer,

    CopyItemQuantities = function(value: ItemQuantities): ItemQuantities
        return deepCopy(value)
    end,
    CopyPlayerView = function(value: PlayerView): PlayerView
        return deepCopy(value)
    end,
    CopySessionView = function(value: SessionView): SessionView
        return deepCopy(value)
    end,
    CopyWorldView = function(value: WorldView): WorldView
        return deepCopy(value)
    end,
    CopySnapshot = function(value: Snapshot): Snapshot
        return deepCopy(value)
    end,
    CopyGetSnapshotResponse = function(value: GetSnapshotResponse): GetSnapshotResponse
        return deepCopy(value)
    end,
    CopyInteractionOpened = function(value: InteractionOpened): InteractionOpened
        return deepCopy(value)
    end,
    CopyActionResult = function(value: ActionResult): ActionResult
        return deepCopy(value)
    end,
    CopyStateDelta = function(value: StateDelta): StateDelta
        return deepCopy(value)
    end,
}

return deepFreeze(NetTypes)
