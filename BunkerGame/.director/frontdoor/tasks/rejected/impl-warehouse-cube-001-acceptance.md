"# Acceptance criteria: impl-warehouse-cube-001

PASS requires ALL of:
1. A valid .rbxm file exists containing a Model named AbandonedWarehouse with 50+ Part children (cube-based, not a single MeshPart).
2. A .model.json file exists in src/Workspace/ following the existing format pattern.
3. The .rbxm was uploaded to Roblox via the API key and a Roblox asset ID was returned (report the ID).
4. The existing GLB warehouse at assets/source/abandoned_warehouse/ was NOT modified.
5. No full API key value was printed in any output.
6. The warehouse uses dark, desaturated colors appropriate for an abandoned industrial structure.
7. The generator script is saved in tools/ for reproducibility."