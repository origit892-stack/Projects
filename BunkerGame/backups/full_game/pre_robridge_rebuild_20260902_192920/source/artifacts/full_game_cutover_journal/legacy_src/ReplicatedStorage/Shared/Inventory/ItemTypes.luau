export type ItemId = string

export type StackPolicy = {
    Stackable: boolean,
    MaxQuantity: number?,
}

export type ItemPresentation = {
    DisplayName: string?,
    Icon: string?,
}

export type ItemDefinition = {
    Id: ItemId,
    Category: string,
    StackPolicy: StackPolicy,
    Tags: { string }?,
    Presentation: ItemPresentation?,
    GameplayRef: string?,
}

export type InventoryEntryView = {
    ItemId: ItemId,
    Quantity: number,
}

export type InventoryView = {
    Entries: { InventoryEntryView },
}

export type InventoryResult = {
    Success: boolean,
    Code: string,
    ItemId: ItemId?,
    Quantity: number?,
}

return table.freeze({})
