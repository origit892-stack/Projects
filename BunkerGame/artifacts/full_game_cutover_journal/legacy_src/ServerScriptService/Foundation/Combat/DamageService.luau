local Players = game:GetService("Players")

local CombatStateService = require(script.Parent.CombatStateService)

local DamageService = {}

local function failure(code: string)
    return table.freeze({
        Success = false,
        Code = code,
        AppliedAmount = 0,
    })
end

function DamageService.Apply(request)
    if type(request) ~= "table" then
        return failure("INVALID_REQUEST")
    end
    if type(request.DamageSourceId) ~= "string" or request.DamageSourceId == "" then
        return failure("INVALID_DAMAGE_SOURCE")
    end
    local payload = request.AuthoritativeDamagePayload
    if type(payload) ~= "table" or type(payload.Amount) ~= "number" then
        return failure("INVALID_DAMAGE_PAYLOAD")
    end

    local targetActor = request.TargetActor
    if typeof(targetActor) ~= "Instance" then
        return failure("INVALID_TARGET")
    end

    local targetPlayer = Players:GetPlayerFromCharacter(targetActor)
    if not targetPlayer then
        return failure("UNSUPPORTED_TARGET")
    end

    -- This is an internal server-domain API. A future client weapon protocol must
    -- resolve trusted damage server-side before constructing this request.
    return CombatStateService.ApplyHealthDamage(targetPlayer, payload.Amount)
end

return table.freeze(DamageService)
