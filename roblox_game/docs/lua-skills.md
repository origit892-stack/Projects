# Luau/ Lua for Roblox — Professional Programming Skills

## File Structure (Roblox Official Style)

```
1. Block comment (why this file exists)
2. Services (game:GetService)
3. Module imports (require)
4. Module-level constants
5. Module-level variables and functions
6. The object the module returns
7. Return statement
```

### Service & Import Organization
```lua
--!strict

-- Services (alphabetical)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")

-- Module imports (alphabetical)
local MathUtils = require(ReplicatedStorage.Shared.MathUtils)
local Trove = require(ReplicatedStorage.Shared.Trove)
```

**Rules:**
- All `require()` calls at the top (static dependencies)
- Sorted alphabetically by module name
- Use `game:GetService()` — never `game.Workspace`
- Module paths absolute from root service (e.g., `ReplicatedStorage.Shared.X`)
- Never use dynamic requires

## Strict Typing

```lua
--!strict

-- Always annotate function signatures and return types
local function calculateDamage(base: number, multiplier: number): number
    return base * multiplier
end

-- Use export type for shared types across modules
export type WeaponData = {
    name: string,
    damage: number,
    range: number,
    cooldown: number,
}

-- Read-only properties (new type solver)
export type Config = {
    read maxPlayers: number,
    read version: string,
    write onUpdate: () -> (),
}

-- Optional types
local function findPlayer(name: string): Player?
    return Players:FindFirstChild(name) :: Player?
end
```

**Rules:**
- `--!strict` on every new file
- `--!nonstrict` on legacy files being migrated
- `any` type disallowed except where functionality demands it
- Union types (`|`) and intersections (`&`) used sparingly with justification

## Module Pattern (Singletons)

Roblox caches the return value of a ModuleScript after first `require()`. Every subsequent `require()` returns the same table —天然 singletons.

```lua
--!strict
local CombatService = {}
CombatService.__index = CombatService

-- Private state
local connections: {RBXScriptConnection} = {}
local activePlayers: {[number]: boolean} = {}

function CombatService.init()
    -- Public API
end

function CombatService.damage(attacker: Player, target: Player, amount: number)
    -- Implementation
end

return CombatService
```

**Rules:**
- Named variable + return (not returning anonymous table)
- Private state via local variables, not underscore prefixes
- One module per file
- Prefer individual files over huge utility libraries

## Observer Pattern (Custom Signals)

```lua
--!strict
export type Signal<T...> = {
    connect: (self: Signal<T...>, callback: (T...) -> ()) -> Connection,
    fire: (self: Signal<T...>, T...) -> (),
    disconnect: (self: Signal<T...>) -> (),
}

export type Connection = {
    disconnect: (self: Connection) -> (),
}

local function createSignal<T...>(): Signal<T...>
    local listeners: {(T...) -> ()} = {}

    local signal = {} :: Signal<T...>

    function signal:connect(callback: (T...) -> ())
        table.insert(listeners, callback)
        return {
            disconnect = function(self)
                local idx = table.find(listeners, callback)
                if idx then table.remove(listeners, idx) end
            end,
        }
    end

    function signal:fire(T...)
        for _, listener in listeners do
            listener(T...)
        end
    end

    return signal
end
```

**When to use:**
- **BindableEvents** — server-to-server decoupling
- **RemoteEvents** — server-client messaging
- **Custom signals** — typed, no Instance overhead, faster than BindableEvents

**Critical:** Always store connection objects and call `:Disconnect()` when done. Memory leaks from orphaned connections are the #1 silent performance killer.

## State Machine

```lua
--!strict

export type State = {
    enter: () -> (),
    update: (dt: number) -> (),
    exit: () -> (),
}

export type StateMachine = {
    current: string?,
    states: {[string]: State},
    transition: (self: StateMachine, newState: string) -> (),
    update: (self: StateMachine, dt: number) -> (),
}

local function createStateMachine(): StateMachine
    local sm = {} :: StateMachine
    sm.states = {}
    sm.current = nil

    function sm:transition(newState: string)
        if self.current then
            local state = self.states[self.current]
            if state then state.exit() end
        end
        self.current = newState
        local state = self.states[newState]
        if state then state.enter() end
    end

    function sm:update(dt: number)
        if self.current then
            local state = self.states[self.current]
            if state then state.update(dt) end
        end
    end

    return sm
end
```

**Use for:** Round-based loops, NPC AI, combat states, door logic, UI screen flows.

**Define explicit transition map** — which states can go to which other states. Log warnings on illegal transitions.

## Service Locator

```lua
--!strict
-- ReplicatedStorage.Shared.ServiceLocator

local ServiceLocator = {}
local services: {[string]: any} = {}

function ServiceLocator.register(name: string, service: any)
    services[name] = service
end

function ServiceLocator.get(name: string): any
    local service = services[name]
    assert(service, `[ServiceLocator] Service "{name}" not registered`)
    return service
end

return ServiceLocator
```

**Use for:** Decoupling scripts from file system layout, easier testing with mock services, single initialization point.

## Dependency Injection

```lua
--!strict

export type CombatService = {
    new: (deps: {dataStore: any, analytics: any}) -> CombatService,
}

local function CombatService(deps: {dataStore: any, analytics: any}): CombatService
    local self = {}
    local dataStore = deps.dataStore
    local analytics = deps.analytics

    function self.damage(amount: number)
        -- use injected dependencies
    end

    return self
end
```

## Parallel Luau (Actors)

```lua
-- Actor contains scripts that run in parallel
-- Scripts inside Actor CANNOT access Instances outside during parallel phase
-- Must call task.synchronize() to modify DataModel

local Actor = Instance.new("Actor")
Actor.Parent = workspace

-- Inside Actor's script:
task.desynchronize() -- enter parallel phase
-- CPU-bound work: pathfinding, spatial queries, procedural gen
local result = heavyComputation()
task.synchronize() -- back to main thread
-- Apply result to DataModel
```

**Use for:** Pathfinding, spatial hashing, procedural generation, AI decision trees. Not for general-purpose threading.

## Error Handling

```lua
--!strict

-- pcall for external operations
local function saveData(player: Player, data: {[string]: any}): boolean
    local success, err = pcall(function()
        dataStore:SetAsync(`player_{player.UserId}`, data)
    end)
    if not success then
        warn(`[DataStore] Failed to save for {player.Name}: {err}`)
    end
    return success
end

-- xpcall with traceback
local ok, result = xpcall(function()
    riskyOperation()
end, function(e: any): string
    return debug.traceback(tostring(e))
end)

-- Structured logging
local function logError(system: string, operation: string, entity: string, err: string)
    warn(`[{system}] {operation} failed for {entity}: {err}`)
end
```

**Wrap in pcall:** DataStore calls, HttpService requests, player input processing, asset loading.

## Luau-Specific Features

### String Interpolation
```lua
local name = "World"
print(`Hello, {name}!`) -- backtick strings
```

### if Expressions (use over `x and y or z`)
```lua
local status = if health > 0 then "alive" else "dead"

-- Multi-condition (use sparingly)
local tier = if score > 1000 then "gold"
    elseif score > 500 then "silver"
    else "bronze"
```

### Generalized Iteration
```lua
for _, child in workspace:GetChildren() do -- no ipairs needed
    print(child.Name)
end
```

### Table Utilities
```lua
table.insert(array, value)
table.remove(array, index)
table.find(array, value) -- returns index or nil
table.freeze(myTable) -- immutable
```

### UDim2 Constructors
```lua
-- Prefer these over UDim2.new(scale, offset, scale, offset)
UDim2.fromScale(0.5, 0.5)
UDim2.fromOffset(200, 100)
```

## Memory Leak Prevention

1. **Always `:Destroy()` Instances** you create when done
2. **Always `:Disconnect()` connections** when listener is no longer needed
3. **Clear table references** — `table.clear(myTable)` or set to `{}`
4. **Remove metatables** — `setmetatable(tbl, nil)` when done
5. **Use weak tables** for caches: `setmetatable({}, { __mode = "k" })`
6. **Test and measure** — use MicroProfiler to find leaks

```lua
-- Cleanup pattern
local connections: {RBXScriptConnection} = {}

local conn = someEvent:Connect(function() end)
table.insert(connections, conn)

-- On cleanup:
for _, conn in connections do
    conn:Disconnect()
end
table.clear(connections)
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Local variables | camelCase | `local healthPoints` |
| Functions | camelCase | `local function calculateDamage()` |
| Modules/PascalCase | PascalCase | `CombatService` |
| Constants | SCREAMING_SNAKE | `local MAX_HEALTH = 100` |
| Booleans | is/has/can prefix | `local isAlive` |
| Events | past tense | `PlayerDamaged`, `RoundStarted` |
| Private | underscore prefix (optional) | `local _cache = {}` |

**Rules:**
- No abbreviations — `healthPoints` not `hp`
- Semantic duplication — if variable's role changes, create new variable
- No magic numbers — define as named constants

## Metatable Guidelines (Roblox Official)

**Limit use to:**
1. OOP class definitions (with `__index`)
2. Custom enum-like tables (throw on invalid index)

```lua
-- OOP class
export type MyClass = {
    new: (name: string) -> MyClass,
    getName: (self: MyClass) -> string,
}

local MyClass = {}
MyClass.__index = MyClass

function MyClass.new(name: string): MyClass
    return setmetatable({ _name = name }, MyClass)
end

function MyClass.getName(self: MyClass): string
    return self._name
end
```

**Never use for:** Simple data tables, caching, or anything that can be done with plain tables.

## Performance Tips

1. **GETIMPORT optimization** — Luau VM resolves non-mutated globals at load time. Keep globals non-mutated for fast paths.
2. **Avoid `print()` in production** — it's slower than you think
3. **DUPCLOSURE** — define functions outside loops to reuse closures
4. **Use `--!optimize 2`** for production (enables inlining)
5. **Minimize DataModel access in tight loops** — cache references
6. **`task.wait()` not `wait()`** — `wait()` is deprecated

## Testing (TestEZ)

```lua
--!strict
local TestEZ = require(ReplicatedStorage.Shared.TestEZ)

return function()
    describe("CombatService", function()
        it("should calculate damage correctly", function()
            local result = CombatService.calculateDamage(100, 1.5)
            expect(result).to.equal(150)
        end)

        it("should not allow negative damage", function()
            expect(function()
                CombatService.calculateDamage(-10, 1)
            end).to.throw()
        end)
    end)
end
```

**Test:** Core services, data validation, state machine transitions, edge cases.

## Best Practices Summary

1. `--!strict` on every new file
2. Guard clause pattern — check nil early, return immediately
3. Never trust client input — validate on server
4. `task.wait()` not `wait()`
5. Prefer `:FindFirstChild()` over `:WaitForChild()` when possible
6. Use `pcall` for external calls
7. No global variables
8. RemoteEvents for cross-boundary communication
9. Clean up connections
10. Name your threads for debugging

## References

- [Roblox Lua Style Guide](https://roblox.github.io/lua-style-guide/)
- [Luau Type System Guide](https://www.oflight.co.jp/en/columns/luau-type-system-strict-mode-guide-2026)
- [Luau Scripting Patterns](https://simplified.media/guides/luau-scripting-patterns)
- [Kampfkarren's Guidelines](https://github.com/Kampfkarren/kampfkarren-luau-guidelines)
- [Luau Optimizations](https://devforum.roblox.com/t/luau-optimizations-and-using-them-consciously/3631483)
- [Advanced Scripting Tutorial](https://devforum.roblox.com/t/advanced-scripting-tutorial/3511460)