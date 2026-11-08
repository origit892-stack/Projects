# Acceptance: verify bunker-rooms Studio sync readiness
PASS requires all 5 items verified with concrete evidence:
1. model.json valid, Model named bunker-rooms, 10 MeshParts each with rbxassetid:// MeshId + Size + Position + Anchored.
2. Spot-check of >=3 Roblox Mesh asset ids (live/Approved, or UNKNOWN if no auth).
3. argon serve running + LISTENING on port 8000 (PID reported).
4. Studio<->Argon connection state (CONNECTED / NOT_CONNECTED) via lsof ESTABLISHED.
5. default.project.json src/Workspace -> workspace mapping confirmed.
Plus a SUMMARY with the BOTTOM LINE (will user see it now, or reconnect needed + exact action).
FAIL if any item is missing or lacks concrete evidence.
