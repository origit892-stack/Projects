export type LifecycleState = "Alive" | "Downed" | "Dead"

export type HealthView = {
    Current: number,
    Maximum: number,
}

export type PlayerCombatView = {
    LifecycleState: LifecycleState,
    Health: HealthView?,
}

export type DamageRequest = {
    SourceActor: Instance?,
    TargetActor: Instance,
    DamageSourceId: string,
    AuthoritativeDamagePayload: {
        Amount: number,
    },
    Context: any?,
}

export type DamageResult = {
    Success: boolean,
    Code: string,
    AppliedAmount: number,
    ResultingLifecycleState: LifecycleState?,
}

export type WeaponId = string

export type WeaponDefinition = {
    Id: WeaponId,
    ItemId: string?,
}

return table.freeze({})
