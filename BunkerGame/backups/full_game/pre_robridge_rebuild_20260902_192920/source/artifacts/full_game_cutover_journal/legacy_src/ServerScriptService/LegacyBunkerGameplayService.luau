local LegacyBunkerGameplayService = {}

local function getStat(player: Player, name: string): IntValue?
    local leaderstats = player:FindFirstChild("leaderstats")
    local value = leaderstats and leaderstats:FindFirstChild(name)
    return value and value:IsA("IntValue") and value or nil
end

local function result(success: boolean, code: string)
    return table.freeze({ Success = success, Code = code })
end

local handlers = {
    legacy_battery_station = function(player: Player)
        local credits = getStat(player, "Credits")
        local batteries = getStat(player, "Batteries")
        if not credits or not batteries then return result(false, "STATE_NOT_READY") end
        if credits.Value < 20 then return result(false, "INSUFFICIENT_CREDITS") end
        credits.Value -= 20
        batteries.Value += 1
        return result(true, "BATTERY_PURCHASED")
    end,
    legacy_scrap_processor = function(player: Player)
        local scrap = getStat(player, "Scrap")
        local credits = getStat(player, "Credits")
        if not scrap or not credits then return result(false, "STATE_NOT_READY") end
        if scrap.Value <= 0 then return result(false, "NO_SCRAP") end
        credits.Value += scrap.Value * 5
        scrap.Value = 0
        return result(true, "SCRAP_PROCESSED")
    end,
    legacy_harvest_upgrade = function(player: Player)
        local credits = getStat(player, "Credits")
        if not credits then return result(false, "STATE_NOT_READY") end
        if player:GetAttribute("HarvestPower") == 2 then return result(false, "ALREADY_UPGRADED") end
        if credits.Value < 100 then return result(false, "INSUFFICIENT_CREDITS") end
        credits.Value -= 100
        player:SetAttribute("HarvestPower", 2)
        return result(true, "HARVEST_UPGRADED")
    end,
    legacy_weapon_upgrade = function(player: Player)
        local credits = getStat(player, "Credits")
        if not credits then return result(false, "STATE_NOT_READY") end
        if credits.Value < 200 then return result(false, "INSUFFICIENT_CREDITS") end
        credits.Value -= 200
        player:SetAttribute("GunDamage", (player:GetAttribute("GunDamage") or 20) + 10)
        return result(true, "WEAPON_UPGRADED")
    end,
}

function LegacyBunkerGameplayService.TryInteract(player: Player, gameplayTargetId: string)
    local handler = handlers[gameplayTargetId]
    if not handler then return result(false, "UNKNOWN_TARGET") end
    return handler(player)
end

return table.freeze(LegacyBunkerGameplayService)
