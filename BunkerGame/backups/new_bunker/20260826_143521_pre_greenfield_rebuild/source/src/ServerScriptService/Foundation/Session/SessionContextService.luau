local Players = game:GetService("Players")

local SessionContextService = {}

local membership: { [Player]: boolean } = {}

local function isEligible(player: Player): boolean
    return player.Parent == Players and membership[player] == true
end

local function addPlayer(player: Player)
    membership[player] = true
end

local function removePlayer(player: Player)
    membership[player] = nil
end

for _, player in Players:GetPlayers() do
    addPlayer(player)
end

Players.PlayerAdded:Connect(addPlayer)
Players.PlayerRemoving:Connect(removePlayer)

function SessionContextService.IsActivePlayer(player: Player): boolean
    return isEligible(player)
end

function SessionContextService.GetActivePlayersSnapshot(): { Player }
    local snapshot = {}
    for player in membership do
        if isEligible(player) then
            table.insert(snapshot, player)
        end
    end
    table.sort(snapshot, function(a, b)
        return a.UserId < b.UserId
    end)
    return snapshot
end

function SessionContextService.GetActivePlayerCount(): number
    local count = 0
    for player in membership do
        if isEligible(player) then
            count += 1
        end
    end
    return count
end

function SessionContextService.GetPlayerSessionState(player: Player)
    return table.freeze({
        UserId = player.UserId,
        Active = isEligible(player),
    })
end

function SessionContextService.GetSnapshot()
    local players = {}
    for _, player in SessionContextService.GetActivePlayersSnapshot() do
        table.insert(players, SessionContextService.GetPlayerSessionState(player))
    end
    return table.freeze({
        ActivePlayerCount = #players,
        Players = table.freeze(players),
    })
end

return table.freeze(SessionContextService)
