local Players = game:GetService("Players")

local CombatStateService = {}

local lifecycleByPlayer: { [Player]: string } = {}

local function getHumanoid(player: Player): Humanoid?
    local character = player.Character
    if not character then
        return nil
    end
    return character:FindFirstChildOfClass("Humanoid")
end

local function inferLifecycle(player: Player): string
    local explicit = lifecycleByPlayer[player]
    if explicit == "Downed" or explicit == "Dead" then
        return explicit
    end
    local humanoid = getHumanoid(player)
    if humanoid and humanoid.Health <= 0 then
        return "Dead"
    end
    return "Alive"
end

function CombatStateService.GetView(player: Player)
    local humanoid = getHumanoid(player)
    local healthView = nil
    if humanoid then
        healthView = table.freeze({
            Current = humanoid.Health,
            Maximum = humanoid.MaxHealth,
        })
    end
    return table.freeze({
        LifecycleState = inferLifecycle(player),
        Health = healthView,
    })
end

function CombatStateService.SetLifecycleState(player: Player, lifecycleState: string)
    if player.Parent ~= Players then
        return table.freeze({ Success = false, Code = "PLAYER_NOT_ACTIVE" })
    end
    if lifecycleState ~= "Alive" and lifecycleState ~= "Downed" and lifecycleState ~= "Dead" then
        return table.freeze({ Success = false, Code = "INVALID_LIFECYCLE_STATE" })
    end
    lifecycleByPlayer[player] = lifecycleState
    return table.freeze({ Success = true, Code = "OK" })
end

function CombatStateService.ApplyHealthDamage(player: Player, amount: number)
    if player.Parent ~= Players then
        return table.freeze({ Success = false, Code = "PLAYER_NOT_ACTIVE", AppliedAmount = 0 })
    end
    if amount ~= amount or amount <= 0 or amount == math.huge then
        return table.freeze({ Success = false, Code = "INVALID_DAMAGE", AppliedAmount = 0 })
    end
    local humanoid = getHumanoid(player)
    if not humanoid or humanoid.Health <= 0 then
        return table.freeze({ Success = false, Code = "TARGET_NOT_DAMAGEABLE", AppliedAmount = 0 })
    end
    local before = humanoid.Health
    humanoid:TakeDamage(amount)
    local applied = math.max(0, before - humanoid.Health)
    if humanoid.Health <= 0 then
        lifecycleByPlayer[player] = "Dead"
    end
    return table.freeze({
        Success = true,
        Code = "OK",
        AppliedAmount = applied,
        ResultingLifecycleState = inferLifecycle(player),
    })
end

local function resetPlayer(player: Player)
    lifecycleByPlayer[player] = "Alive"
end

for _, player in Players:GetPlayers() do
    resetPlayer(player)
    player.CharacterAdded:Connect(function()
        resetPlayer(player)
    end)
end

Players.PlayerAdded:Connect(function(player)
    resetPlayer(player)
    player.CharacterAdded:Connect(function()
        resetPlayer(player)
    end)
end)

Players.PlayerRemoving:Connect(function(player)
    lifecycleByPlayer[player] = nil
end)

return table.freeze(CombatStateService)
