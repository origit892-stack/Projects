# Research: Why can't the user see the bunker in Roblox Studio?

The user just said: "i dont see the folder or the bunker." They are looking at Roblox Studio and cannot find the bunker. Determine the cause.

## Verified facts (already known — do NOT re-derive these)
- Project root: /Users/Ori/Documents/Projects/BunkerGame
- Active source files:
  - src/Workspace/bunker-rooms.model.json  (Model "bunker-rooms": 10 room MeshParts at Y≈54 + a Foundation Part, top Y=54.0)
  - src/Workspace/SpawnRoot.model.json     (Model "SpawnRoot" → SpawnLocation "PlayerSpawn" at [0,54.5,-10])
- default.project.json maps Workspace → src/Workspace
- Ground datum from a prior task: GROUND_TOP_Y = 54.0, but the custom ground slab that used to sit there was DELETED in that prior task.
- argon serve was previously live on 127.0.0.1:8000.

## Do EXACTLY these 4 checks, in order

CHECK 1 — Is argon running right now?
Run: ps aux | grep -i argon | grep -v grep
Run: lsof -nP -iTCP:8000 -sTCP:LISTEN
Report: is the argon process present? Is port 8000 listening? (quote the output)

CHECK 2 — Are the source files valid and complete?
Run: python3 -c "import json; d=json.load(open('src/Workspace/bunker-rooms.model.json')); print('bunker-rooms OK, children:', len(d.get('Children',[])))"
Run: python3 -c "import json; d=json.load(open('src/Workspace/SpawnRoot.model.json')); print('SpawnRoot OK')"
Report: do both parse? How many children does bunker-rooms have?

CHECK 3 — Where is the bunker in Y?
Run: python3 -c "import json; d=json.load(open('src/Workspace/bunker-rooms.model.json')); [print(c['Name'], c['Properties'].get('Position'), c['Properties'].get('Size')) for c in d.get('Children',[])]"
Report: list each child's Name, Position, Size. State the bunker base Y and top Y.

CHECK 4 — Is there a Roblox Folder the user might mean?
Run: grep -c '"Folder"' src/Workspace/bunker-rooms.model.json src/Workspace/SpawnRoot.model.json
Report: how many Folder instances exist in the source (0 is a valid answer)?

## CRITICAL OUTPUT REQUIREMENT
After the 4 checks, your VERY LAST output MUST be exactly this block, filled in. Do not put anything after it. Do not skip it. This is mandatory.
<AGENT_HANDOFF>
STATUS: PASS
TASK_ID: research-bunker-visibility
EXECUTED: CHECK1 argon=<running/not>; CHECK2 json=<valid/invalid>; CHECK3 bunker Y=<base..top>; CHECK4 folders=<N>
RESULT: <one or two sentences: the most likely reason the user cannot see the bunker>
FILES_CHANGED: none
ARTIFACTS: src/Workspace/bunker-rooms.model.json, src/Workspace/SpawnRoot.model.json
VERIFICATION: <the exact command outputs you relied on, briefly>
BLOCKERS: NONE
</AGENT_HANDOFF>