export type PlayerSessionState = {
    UserId: number,
    Active: boolean,
}

export type SessionView = {
    ActivePlayerCount: number,
    Players: { PlayerSessionState },
}

return table.freeze({})
