---
name: BDS analysis profiles
alwaysApply: true
---

# BDS Analysis Profiles

When the user asks about the farming system:

1. Use the terminal tool.
2. Run:
   `bds analyze farming`
3. Treat the BDS output as the primary source of truth.
4. Use `bds range <path> <start> <end>` only when exact implementation detail is required.
5. Do not reinterpret `ProximityPrompt.Triggered` as a RemoteEvent or client-to-server networking.
6. Do not claim client requests exist unless `FireServer`, `InvokeServer`, `OnServerEvent`, or `OnServerInvoke` is present.
7. Respond in Hebrew when the user writes in Hebrew.
8. Do not modify files unless explicitly requested.

## Evidence-bound risk analysis

A risk must be tied to exact evidence.

Do not report these as risks unless direct evidence exists:

- Missing player validation for `FireClient`
- Missing input validation when no client-to-server remote exists
- Missing `Inventory` checks when the code uses `FindFirstChild` and nil guards
- Missing `leaderstats` checks when the code checks or waits for it
- Missing `PlotState` checks when a default value is returned
- Missing RemoteEvent existence checks when the client uses `WaitForChild`
- Infinite-loop risk merely because a periodic server loop is intentionally long-running
- Performance risk merely because `task.spawn` or `task.wait` appears

For every risk, include:
1. Exact file path
2. Exact line number
3. Concrete failure or exploit scenario
4. Why current guards do not prevent it

If those four items cannot be provided, label the item:
`Unverified concern`

