export type InteractionContext = {
    Player: Player,
    InteractionKind: string,
    ResolvedTarget: Instance,
    GameplayTargetId: string?,
    Prompt: ProximityPrompt,
}

export type GameplayInteractionResult = {
    Success: boolean,
    Code: string,
    FeedbackTone: string?,
}

local GameplayInteractionTypes = {
    ResultCode = table.freeze({
        Ok = "OK",
        Unavailable = "UNAVAILABLE",
        NoHandler = "NO_HANDLER",
    }),
}

return table.freeze(GameplayInteractionTypes)
