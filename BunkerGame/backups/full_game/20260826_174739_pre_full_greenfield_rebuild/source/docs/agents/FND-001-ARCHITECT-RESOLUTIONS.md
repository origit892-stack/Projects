# FND-001 Architect Review Resolutions

**Role:** Gameplay Systems Architect  
**Input:** `FND-001-TECHNICAL-REVIEW.md`

## R-DMG-001 — RESOLVED
`DamageRequest` is now explicitly an internal server-domain request. Trusted damage payload provenance must be authoritative server-side; future client weapon intent is a separate protocol.

## R-INT-001 — RESOLVED
Interaction context now distinguishes a server-resolved runtime target from an optional stable gameplay-domain ID. FND-004 is not required to assign global persistent IDs to every world prop.

## R-SES-001 — RESOLVED
Session membership is now an immutable/snapshot read view. Multiplayer / Session owns active-player eligibility and the count is derived from that same rule. Wave consumers may not independently redefine eligibility.

## R-HEALTH-001 — RESOLVED
Combat state now separates lifecycle status from optional numeric HealthView representation. FND-003 chooses concrete numeric/adaptor shape without changing ownership.

## Scope
No runtime code, balance values, feature content, or protected legacy systems were changed.
