# SVS-001 Architect Review Resolutions

**Role:** World / Survival Systems Architect

## R-AXE-001 — RESOLVED
Canonical `axe_basic` possession is now established through InventoryService before a server-owned prototype equipment adapter provisions the physical Tool. Tool presence is never inventory authority. Harvest use validates canonical possession plus the equipped approved Tool.

## R-REWARD-001 — RESOLVED
The resource lifecycle now includes a server-only RewardPending commit state. The final accepted hit reserves one winner/cycle before grant. Further hits cannot win that cycle. Successful InventoryService grant commits once; grant failure remains retryable for the same recorded winner without selecting another winner or creating another inventory representation.

No Foundation contract change is required.
