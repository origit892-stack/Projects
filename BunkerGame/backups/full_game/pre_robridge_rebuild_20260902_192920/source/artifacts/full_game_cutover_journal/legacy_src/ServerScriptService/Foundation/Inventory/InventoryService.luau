local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ItemDefinitions = require(ReplicatedStorage.Shared.Inventory.ItemDefinitions)

local InventoryService = {}

local inventories: { [Player]: { [string]: number } } = {}

local function result(success: boolean, code: string, itemId: string?, quantity: number?)
    return table.freeze({
        Success = success,
        Code = code,
        ItemId = itemId,
        Quantity = quantity,
    })
end

local function validQuantity(quantity: number): boolean
    return quantity == quantity and quantity > 0 and quantity < math.huge and quantity % 1 == 0
end

local function getState(player: Player): { [string]: number }?
    return inventories[player]
end

local function validate(player: Player, itemId: string, quantity: number)
    if player.Parent ~= Players then
        return result(false, "PLAYER_NOT_ACTIVE", itemId)
    end
    if type(itemId) ~= "string" or itemId == "" then
        return result(false, "INVALID_ITEM_ID")
    end
    if not ItemDefinitions.isDefined(itemId) then
        return result(false, "UNKNOWN_ITEM", itemId)
    end
    if not validQuantity(quantity) then
        return result(false, "INVALID_QUANTITY", itemId)
    end
    if not getState(player) then
        return result(false, "INVENTORY_NOT_READY", itemId)
    end
    return nil
end

function InventoryService.GetQuantity(player: Player, itemId: string): number
    local state = getState(player)
    if not state then
        return 0
    end
    return state[itemId] or 0
end

function InventoryService.CanAdd(player: Player, itemId: string, quantity: number)
    local failure = validate(player, itemId, quantity)
    if failure then
        return failure
    end
    return result(true, "OK", itemId, quantity)
end

function InventoryService.Add(player: Player, itemId: string, quantity: number, _context: any?)
    local allowed = InventoryService.CanAdd(player, itemId, quantity)
    if not allowed.Success then
        return allowed
    end
    local state = getState(player) :: { [string]: number }
    state[itemId] = (state[itemId] or 0) + quantity
    return result(true, "OK", itemId, state[itemId])
end

function InventoryService.CanRemove(player: Player, itemId: string, quantity: number)
    local failure = validate(player, itemId, quantity)
    if failure then
        return failure
    end
    if InventoryService.GetQuantity(player, itemId) < quantity then
        return result(false, "INSUFFICIENT_QUANTITY", itemId, InventoryService.GetQuantity(player, itemId))
    end
    return result(true, "OK", itemId, quantity)
end

function InventoryService.Remove(player: Player, itemId: string, quantity: number, _context: any?)
    local allowed = InventoryService.CanRemove(player, itemId, quantity)
    if not allowed.Success then
        return allowed
    end
    local state = getState(player) :: { [string]: number }
    state[itemId] -= quantity
    if state[itemId] == 0 then
        state[itemId] = nil
    end
    return result(true, "OK", itemId, state[itemId] or 0)
end

function InventoryService.GetSnapshot(player: Player)
    local state = getState(player)
    local entries = {}
    if state then
        for itemId, quantity in state do
            table.insert(entries, table.freeze({ ItemId = itemId, Quantity = quantity }))
        end
        table.sort(entries, function(a, b)
            return a.ItemId < b.ItemId
        end)
    end
    return table.freeze({ Entries = table.freeze(entries) })
end

local function initializePlayer(player: Player)
    if inventories[player] == nil then
        inventories[player] = {}
    end
end

for _, player in Players:GetPlayers() do
    initializePlayer(player)
end

Players.PlayerAdded:Connect(initializePlayer)
Players.PlayerRemoving:Connect(function(player)
    inventories[player] = nil
end)

return table.freeze(InventoryService)
