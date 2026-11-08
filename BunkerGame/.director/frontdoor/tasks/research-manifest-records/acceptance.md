# Acceptance Criteria: research-manifest-records (focused)

PASS requires:
1. A complete list of every WorldManifest record/table (with line numbers), grouped by
   category (StableGround, RequiredFolders, Spawns, Stations, Objectives, EnemySpawns,
   Farm, Resources, other), with record names and expected path/class/position.
2. For each record category, the consuming service(s) (file + line) and whether absence
   is handled gracefully or hard-errors.
3. A clear KEEP vs REMOVE recommendation for a bunker-only world that makes
   validateWorld pass without breaking any service.
4. No file modified (read-only).

FAIL if the record list is incomplete, the consumers are not identified, or no
keep/remove recommendation is given.
