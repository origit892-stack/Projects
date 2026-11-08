# Worker Task

TASK_ID=verify-bunker-to-ground

ROLE=verifier

PROJECT_ROOT=/Users/Ori/Documents/Projects/BunkerGame

## Objective

# Verify: Bunker moved to ground level (Y=0)

An implementer just shifted the bunker assembly down by 54 studs so the Foundation top is at Y=0.0 (ground level). Independently verify the changes are correct.

## Verified facts (carry forward — do not re-derive)
- Project root: /Users/Ori/Documents/Projects/BunkerGame
- Source files: src/Workspace/bunker-rooms.model.json, src/Workspace/SpawnRoot.model.json
- Backups: .director/backups/impl-bunker-to-ground/bunker-rooms.model.json.bak, .director/backups/impl-bunker-to-ground/SpawnRoot.model.json.bak
- Expected after shift: Foundation top Y=0.0, room MeshPart bases at Y≈0.0, PlayerSpawn at [0,0.5,-10]

## Do EXACTLY these checks, in order

CHECK 1 — Both files are valid JSON.
Run: python3 -c "import json; json.load(open('src/Workspace/bunker-rooms.model.json')); print('bunker-rooms valid')"
Run: python3 -c "import json; json.load(open('src/Workspace/SpawnRoot.model.json')); print('SpawnRoot valid')"

CHECK 2 — Foundation top is at Y=0.0.
Run: python3 -c "import json; d=json.load(open('src/Workspace/bunker-rooms.model.json')); f=[c for c in d['Children'] if c['Name']=='Foundation'][0]; p=f['Properties']['Position']; s=f['Properties']['Size']; print('Foundation Position:', p, 'Size:', s, 'top Y:', p[1]+s[1]/2)"
Expected: top Y = 0.0 (within 0.01)

CHECK 3 — All 10 room MeshPart bases are at Y≈0.0.
Run: python3 -c "import json; d=json.load(open('src/Workspace/bunker-rooms.model.json')); [print(c['Name'], 'base Y:', c['Properties']['Position'][1]-c['Properties']['Size'][1]/2) for c in d['Children'] if c['ClassName']=='MeshPart']"
Expected: all base Y values within 0.01 of 0.0

CHECK 4 — PlayerSpawn is at [0,0.5,-10].
Run: python3 -c "import json; d=json.load(open('src/Workspace/SpawnRoot.model.json')); s=[c for c in d['Children'] if c['Name']=='PlayerSpawn'][0]; print('PlayerSpawn Position:', s['Properties']['Position'])"
Expected: [0, 0.5, -10]

CHECK 5 — No other properties changed (compare against backups).
Run: diff <(python3 -c "import json; d=json.load(open('.director/backups/impl-bunker-to-ground/bunker-rooms.model.json.bak')); [print(c['Name'], c['Properties'].get('Size'), c['Properties'].get('MeshId'), c['Properties'].get('Anchored'), c['Properties'].get('CanCollide')) for c in d['Children']]") <(python3 -c "import json; d=json.load(open('src/Workspace/bunker-rooms.model.json')); [print(c['Name'], c['Properties'].get('Size'), c['Properties'].get('MeshId'), c['Properties'].get('Anchored'), c['Properties'].get('CanCollide')) for c in d['Children']]")
Expected: no diff (Size, MeshId, Anchored, CanCollide unchanged)

CHECK 6 — Argon is still running (will sync to Studio).
Run: lsof -nP -iTCP:8000 -sTCP:LISTEN
Expected: argon process listening on 127.0.0.1:8000

## CRITICAL OUTPUT REQUIREMENT
Your VERY LAST output MUST be exactly this block, filled in. Do not put anything after it. Do not skip it. This is mandatory.

<AGENT_HANDOFF>
STATUS: PASS or FAIL
TASK_ID: verify-bunker-to-ground
EXECUTED: <list the checks you did>
RESULT: <one or two sentences: all checks passed / which check failed and why>
FILES_CHANGED: none
ARTIFACTS: src/Workspace/bunker-rooms.model.json, src/Workspace/SpawnRoot.model.json
VERIFICATION: <the exact command outputs you relied on, briefly>
BLOCKERS: NONE or <specific blocker>
</AGENT_HANDOFF>

## Write scopes

[]

## Read scopes

["src/Workspace", ".director/backups"]

## Acceptance criteria

# Acceptance Criteria: verify-bunker-to-ground

PASS requires ALL of the following, each backed by VERIFIED_FACT evidence:

1. **Both files valid JSON.** python3 json.load succeeds on both src/Workspace/bunker-rooms.model.json and src/Workspace/SpawnRoot.model.json.
2. **Foundation top at Y=0.0.** The Foundation Part's top surface (Position[1] + Size[1]/2) is within 0.01 of 0.0.
3. **Room MeshPart bases at Y≈0.0.** All 10 room MeshParts have base Y (Position[1] - Size[1]/2) within 0.01 of 0.0.
4. **PlayerSpawn at [0,0.5,-10].** The PlayerSpawn Position is exactly [0, 0.5, -10].
5. **No other properties changed.** Size, MeshId, Anchored, CanCollide are identical between the current files and the backups.
6. **Argon running.** argon serve is listening on 127.0.0.1:8000 (will sync to Studio).
7. **Read-only respected.** No project files were modified, created, or deleted (FILES_CHANGED is none).
8. **Handoff present.** A valid <AGENT_HANDOFF> block is emitted with all required keys.

If any of 1-6 fails, STATUS must be FAIL with the specific check named.

## Rules

Work autonomously until PASS, BLOCKED, or FAILED.
Use your available tools directly.
Do not perform unrelated project work.
Verify before PASS.
Return only the final handoff to the Director.

## Final handoff

<AGENT_HANDOFF>
STATUS=PASS|BLOCKED|FAILED
TASK_ID=<task id>
EXECUTED=<what was performed>
RESULT=<final result>
FILES_CHANGED=<paths or NONE>
ARTIFACTS=<paths/ids or NONE>
VERIFICATION=<objective evidence>
BLOCKERS=<NONE or blocker>
</AGENT_HANDOFF>
