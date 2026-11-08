---
name: Roblox networking and security
globs:
  - "**/*.lua"
  - "**/*.luau"
alwaysApply: false
---

# Roblox Networking and Security

## Server authority

The server must remain authoritative for:

- Currency
- Inventory
- Damage
- Rewards
- Purchases
- Crafting
- Progression
- Saved data
- Ownership
- Cooldowns
- Match and world state

Never trust client-provided values without server validation.

## Remote validation

For every RemoteEvent and RemoteFunction, validate relevant properties such as:

- Player identity
- Current game state
- Ownership
- Distance
- Permissions
- Cooldowns
- Numeric ranges
- String length
- Table shape and depth
- Instance class
- Instance ancestry
- Requested action

Do not let the client directly choose authoritative rewards, prices, damage, inventory quantities, or progression.

## Communication evidence

Do not claim two scripts communicate without explicit evidence such as:

- `RemoteEvent`
- `RemoteFunction`
- `BindableEvent`
- `BindableFunction`
- `require()`
- Shared ModuleScripts
- Direct Instance references
- Attributes
- CollectionService tags
- Matching protocol identifiers
- Explicit shared state

When communication is only suspected, label it as a hypothesis.

## Security reviews

Only report an exploit risk when supported by inspected code.

For each finding, provide:

1. File path
2. Relevant code or behavior
3. Attack or failure scenario
4. Impact
5. Concrete remediation
