# Task: warehouse-research-001 (researcher)

## Objective
Investigate the BunkerGame project to prepare for: (1) creating an abandoned warehouse mesh built from cube parts, and (2) uploading it to Roblox via an API key.

## Project root
/Users/Ori/Documents/Projects/BunkerGame

## Investigate (read-only)
1. Active source tree: top-level structure of src/ and any relevant modules (gameplay, assets, tools).
2. Roblox API key configuration: where an API key is stored (env var name, config file path, .env files). Do NOT print the full key value — report only location, variable name, and format (e.g., first 4 chars + total length).
3. Place ID / game ID: any configured place ID or game ID used for uploads, sync, or deployment.
4. Existing upload scripts: any scripts (Python/Node/shell) that call the Roblox API (apis.roblox.com, assets.roblox.com, places files endpoints, etc.).
5. Existing warehouse/building assets: any existing warehouse, building, structure, or mesh code in src/ or asset folders.
6. Sync workflow: is Argon installed/configured? Is Rojo present (default.project.json)? How does the project currently get into Roblox Studio?
7. Existing .rbxm generation: any code or tooling that generates .rbxm files.

## Constraints
- Read-only. Do not modify any files.
- Do not print full secrets.
- Keep the report compact (under 150 lines).
- Inspect the active src/ tree first; treat backups/artifacts as historical only.

## Output
Compact report with VERIFIED_FACT / INFERENCE / UNKNOWN classifications and exact file paths for every conclusion.