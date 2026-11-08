# Auto Components

Pass `Instance = script` to `Superbullet.CreateService()` or `Superbullet.CreateController()` and the framework loads that system's `Components/` folder for you. You never `require()` a component by hand and never call its `Init()` or `Start()` yourself.

Source of truth: `src/ReplicatedStorage/Packages/_Index/superbullet_knit@0.0.1/knit/Components/ComponentInitializer.lua`. Online version: https://docs.superbulletstudios.com/superbullet-knit/auto-components

> `Superbullet` and `Knit` are the same module. `require(ReplicatedStorage.Packages.Superbullet)` is the primary entry point; `require(ReplicatedStorage.Packages.Knit)` still works. `SuperbulletInit`/`SuperbulletStart` and `KnitInit`/`KnitStart` are interchangeable (the `Superbullet*` name wins if both exist).

## 1. Folder Structure

```
TemplateService/
├── init.lua              << Superbullet.CreateService({ Name = "TemplateService", Instance = script })
└── Components/
    ├── Accessor.lua      << optional: read-only logic   (legacy name: Get().lua)
    ├── Mutator.lua       << optional: write logic       (legacy name: Set().lua)
    └── Others/           << optional: feature modules, any nesting depth
        └── Template.lua
```

Controllers use the exact same layout under `src/ReplicatedStorage/ClientSource/Client/`.

A system without a `Components/` folder is fine. It is skipped silently.

## 2. Where Each Component Ends Up

The framework attaches components to the parent system table:

| File                         | Access from the parent system    | Alias (backward compatibility) |
| ---------------------------- | -------------------------------- | ------------------------------ |
| `Components/Accessor.lua`    | `TemplateService.Accessor`       | `TemplateService.GetComponent` |
| `Components/Mutator.lua`     | `TemplateService.Mutator`        | `TemplateService.SetComponent` |
| `Components/Others/<Name>`   | `TemplateService.Components.<Name>` | —                           |

Important details:

- **`.Components` only holds `Others/` modules.** `Accessor` and `Mutator` are **not** in `.Components`. `TemplateService.Components.Accessor` is `nil`; use `TemplateService.Accessor`.
- **Component functions are not merged into the parent.** Call `TemplateService.Accessor.GetCoins(player)`, not `TemplateService:GetCoins(player)`. If the parent should expose a method, write that method in `init.lua` and have it delegate to the component.
- **`Others/` is keyed by module name only**, across every nested folder. Two modules named `Handler` in different sub-folders overwrite each other. Give every module under `Others/` a unique name.
- `.Components` is only created when an `Others/` folder exists.

## 3. Lifecycle

Order on startup (server and client behave the same):

1. Every service/controller `SuperbulletInit()` runs.
2. For each system with `Instance = script`:
   1. `Others/*`, `Accessor`, and `Mutator` are required and attached (`.Components`, `.Accessor`, `.Mutator`).
   2. `Init()` is called on every component module under `Components/` that defines one.
3. Server only: dynamic remote registration locks (see [dynamic-remotes.md](dynamic-remotes.md)).
4. Every service/controller `SuperbulletStart()` runs, each in its own thread.
5. `Start()` is called on every component that defines one, each in its own thread (deferred until after step 4 has been kicked off).

What this means in practice:

- **`self.Accessor`, `self.Mutator` and `self.Components` are `nil` inside the parent's `SuperbulletInit()`.** They are attached after it. Use them from `SuperbulletStart()`, or from component `Init()`/`Start()`.
- Inside a component's `Init()`, the **parent's own** components are already attached. Another system's components may not be yet, so only touch other systems' components from `Start()`.
- `Init()` and `Start()` are called with **dot syntax and no arguments** (`module.Init()`). They do not receive the parent system; fetch it yourself (see section 4).
- Each component's `Init()`/`Start()` runs once. The framework marks the ModuleScript with `Initialized` / `Started` attributes to prevent double runs.
- Both `Init()` and `Start()` are optional.

### No Yielding in Init

`SuperbulletInit()` and component `Init()` must **never yield**: no `WaitForChild()`, `:await()`, `task.wait()`, `DataStore` calls, or `Promise` waiting. Init blocks the whole framework from finishing startup, and the framework warns after 5 seconds if a `GetService()` call is still waiting on it.

Init is only for:

- `Superbullet.GetService()` / `Superbullet.GetController()` references
- `Superbullet.RegisterClientSignal/Method/Property()` (server)
- Assigning synchronous references and local state

Anything that waits, connects events, or loops belongs in `Start()` (use `task.spawn()` if it yields for long).

## 4. Writing a Component

Components are plain module tables with **dot syntax**. Colon syntax and `self` are only for OOP objects you create with `.new()` inside a component.

```lua
-- TemplateService/Components/Others/RewardHandler.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Superbullet = require(ReplicatedStorage.Packages.Superbullet)
local module = {}

---- Superbullet Services
local TemplateService

---- Components
local Accessor
local Mutator

function module.GrantDailyReward(player: Player)
	if Accessor.HasClaimedToday(player) then
		return false
	end
	Mutator.MarkClaimed(player)
	return true
end

function module.Start()
	-- Runtime logic, event connections, loops
end

function module.Init()
	TemplateService = Superbullet.GetService("TemplateService")

	Accessor = TemplateService.Accessor
	Mutator = TemplateService.Mutator
end

return module
```

On the client, fetch the parent with `Superbullet.GetController("TemplateController")`. `Superbullet.GetService()` on the client returns the server service's **remote** interface, not a local table.

Components also follow the communication rules in [organizing-project-structure.md](../codebase/organizing-project-structure.md#3-component-communication-rules). In particular, `Accessor` and `Mutator` must not call each other directly; coordinate through the parent or an `Others/` component as above.

## 5. Calling Components from the Parent

```lua
-- TemplateService/init.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Superbullet = require(ReplicatedStorage.Packages.Superbullet)

local TemplateService = Superbullet.CreateService({
	Name = "TemplateService",
	Instance = script, -- Automatically initializes components
})

function TemplateService:ClaimDailyReward(player: Player)
	return self.Components.RewardHandler.GrantDailyReward(player)
end

function TemplateService:SuperbulletStart()
	-- self.Accessor / self.Mutator / self.Components are available here
end

function TemplateService:SuperbulletInit()
	-- Do NOT touch self.Accessor / self.Mutator / self.Components here, they are not attached yet
end

return TemplateService
```

For full IntelliSense from another system, require the module instance:

```lua
local TemplateService = require(Superbullet.GetService("TemplateService").Instance)
```

## 6. Errors

- A component whose `Init()` throws logs `Error initializing component <full path>: <error>` and the remaining components keep initializing.
- If a service/controller's `SuperbulletInit()` throws, its components are skipped entirely and its `SuperbulletStart()` never runs. Fix the Init error first.
- A component `Start()` error surfaces as a normal error from its own thread.

## 7. Checklist

- [ ] `Instance = script` is set on `CreateService` / `CreateController`.
- [ ] Components live in `Components/Accessor.lua`, `Components/Mutator.lua`, or `Components/Others/`.
- [ ] Module-level functions use dot syntax; no `self` outside OOP objects.
- [ ] Nothing yields in `Init()` / `SuperbulletInit()`.
- [ ] Parent code reads components in `SuperbulletStart()` or later, never in `SuperbulletInit()`.
- [ ] Accessor/Mutator are reached via `.Accessor` / `.Mutator`, `Others/` via `.Components.<Name>`.
- [ ] Every module name under `Others/` is unique.
