# Dynamic Remotes

Dynamic remotes let a **component** add signals, methods, and properties to its parent service's `Client` table. The framework creates the underlying `RemoteEvent` / `UnreliableRemoteEvent` / `RemoteFunction` and replicates them. You never create remotes by hand in `ReplicatedStorage`.

This keeps each network endpoint next to the component that owns it, so a feature's server-client communication lives in one file instead of piling up in the service's `init.lua`.

Source of truth: `src/ReplicatedStorage/Packages/_Index/superbullet_knit@0.0.1/knit/Components/ClientExtension.lua` (exposed through `KnitServer.lua`). Online version: https://docs.superbulletstudios.com/superbullet-knit/dynamic-remotes

> Server only. Read [auto-components.md](auto-components.md) first; the timing rules below depend on the component lifecycle.

## 1. API

All three take the **service table** (not its name) as the first argument.

### `Superbullet.RegisterClientSignal(service, signalName, unreliable?)`

Creates a RemoteSignal at `service.Client[signalName]` and returns it, so you can chain `:Connect()`. Pass `true` for `unreliable` to use an `UnreliableRemoteEvent` (fine for cosmetic, high-frequency data; delivery is not guaranteed or ordered).

```lua
Superbullet.RegisterClientSignal(InventoryService, "OnItemCollected"):Connect(function(player, itemId)
	-- client fired the signal
end)

-- Fire to clients later:
InventoryService.Client.OnItemCollected:Fire(player, itemId)
InventoryService.Client.OnItemCollected:FireAll(itemId)
```

### `Superbullet.RegisterClientMethod(service, methodName)`

Returns a wrapper. Assign `.OnServerInvoke` once, Roblox-style. Assigning it is what creates the `RemoteFunction`.

```lua
Superbullet.RegisterClientMethod(InventoryService, "GetInventory").OnServerInvoke = function(client, player)
	return Accessor.GetInventory(player)
end
```

The handler receives `(client, player, ...args)`. `client` is the service's `Client` table (`client.Server` is the service itself). `player` is always the calling player, supplied by Roblox; never trust the remaining arguments.

### `Superbullet.RegisterClientProperty(service, propertyName, initialValue)`

Creates a RemoteProperty that replicates to every client, and returns it.

```lua
local configProp = Superbullet.RegisterClientProperty(InventoryService, "MaxSlots", 20)

configProp:Set(30)                 -- all clients
configProp:SetFor(player, 40)      -- one client
print(configProp:Get())
```

## 2. When to Register

Register inside a **component's `Init()`** (preferred) or the service's `SuperbulletInit()`.

| Where you call it                       | Result                                                                 |
| --------------------------------------- | ---------------------------------------------------------------------- |
| Component `Init()`                      | ✅ Correct place                                                       |
| Service `SuperbulletInit()`             | ✅ Works                                                                |
| Service `SuperbulletStart()` / component `Start()` | ❌ Errors: `Cannot register client ... after component Init phase` |
| Module top level (outside any function) | ❌ Don't. Methods registered there get wrapped twice, creating duplicate `RemoteFunction`s |

Registration locks right after every component `Init()` has run and before any `SuperbulletStart()`. The server only marks its services folder `Ready` after that, and clients wait for `Ready` before building service proxies, so every dynamic remote exists by the time any client calls `GetService()`.

## 3. Validation

Each call asserts, with a readable error, that:

- registration is not locked yet;
- the name is a non-empty string;
- the first argument is a real service created with `Superbullet.CreateService()`;
- the name is not already used on `service.Client` (including names declared statically in the `Client = {}` table);
- `OnServerInvoke` is a function and is assigned only once.

## 4. Full Example

```
InventoryService/
├── init.lua
└── Components/
    ├── Accessor.lua
    └── Others/
        └── PickupHandler.lua   << owns the inventory remotes
```

```lua
-- InventoryService/init.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Superbullet = require(ReplicatedStorage.Packages.Superbullet)

local InventoryService = Superbullet.CreateService({
	Name = "InventoryService",
	Client = {},
	Instance = script, -- Automatically initializes components
})

function InventoryService:SuperbulletStart() end

function InventoryService:SuperbulletInit() end

return InventoryService
```

```lua
-- InventoryService/Components/Others/PickupHandler.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Superbullet = require(ReplicatedStorage.Packages.Superbullet)
local module = {}

---- Superbullet Services
local InventoryService

---- Components
local Accessor

---- Datas
local onItemCollected

function module.Start()
	-- Runtime: fire onItemCollected when the server awards an item
	-- onItemCollected:Fire(player, itemId)
end

function module.Init()
	InventoryService = Superbullet.GetService("InventoryService")
	Accessor = InventoryService.Accessor

	onItemCollected = Superbullet.RegisterClientSignal(InventoryService, "OnItemCollected")

	Superbullet.RegisterClientMethod(InventoryService, "GetInventory").OnServerInvoke = function(_client, player)
		return Accessor.GetInventory(player)
	end

	Superbullet.RegisterClientProperty(InventoryService, "MaxSlots", 20)
end

return module
```

## 5. Client Usage

Clients see dynamic remotes exactly like statically declared ones:

```lua
-- Any controller or controller component, in Init() or later
local InventoryService = Superbullet.GetService("InventoryService")

InventoryService.OnItemCollected:Connect(function(itemId)
	print("Collected", itemId)
end)

InventoryService.MaxSlots:Observe(function(maxSlots)
	print("Max slots:", maxSlots)
end)

-- Methods return Promises (ServicePromises is on by default)
InventoryService:GetInventory():andThen(function(inventory)
	print(inventory)
end)
```

`:await()` on a method Promise yields, so only do it from `Start()` / `SuperbulletStart()`, never from `Init()`.

## 6. Security

Every dynamic remote is a public network endpoint. Follow [organizing-project-structure.md](../codebase/organizing-project-structure.md#13-security-best-practices-preventing-exploiters):

- Make remotes **action-based** (`RequestPickup(itemId)`), not value-based (`AddCoins(amount)`).
- Validate every argument on the server; the server decides results and rewards.
- Use unreliable signals only for data the game can afford to lose.

## 7. Checklist

- [ ] Registered inside a component `Init()` (or `SuperbulletInit()`), never in `Start()` or at module top level.
- [ ] First argument is the service table from `Superbullet.GetService()`, not a string.
- [ ] Remote names are unique on that service's `Client` table.
- [ ] `OnServerInvoke` handler signature is `(client, player, ...)`.
- [ ] Server validates every client argument.
- [ ] Client code treats methods as Promises.
