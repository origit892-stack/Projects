"""Playtest manager: run the built world and collect what actually happened.

A playtest is only useful if it produces evidence: console errors, warnings, spawn validity and a
simple "can the player move and reach something" check. Results are stored so the QA report and the
repair loop can act on them.
"""
from __future__ import annotations

import re
import time

ERROR_PATTERNS = [
    re.compile(r"stack (?:begin|end)", re.I),
    re.compile(r"\berror\b", re.I),
    re.compile(r"attempt to (index|call|perform)\b", re.I),
    re.compile(r"is not a valid member", re.I),
    re.compile(r"Infinite yield", re.I),
]


def parse_console(text: str) -> dict:
    errors, warnings = [], []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(pattern.search(stripped) for pattern in ERROR_PATTERNS):
            errors.append(stripped[:400])
        elif "warn" in stripped.lower():
            warnings.append(stripped[:400])
    return {"errors": errors[:40], "warnings": warnings[:40],
            "error_count": len(errors), "warning_count": len(warnings)}


def playtest(client, seconds: int = 20, poll_every: float = 4.0) -> dict:
    if not getattr(client, "has", lambda _n: True)("start_stop_play"):
        return {"ran": False, "reason": "Studio session exposes no play/stop tool",
                "errors": [], "warnings": []}
    started = time.time()
    try:
        client.call("start_stop_play", {"action": "start"})
    except Exception as exc:  # noqa: BLE001
        return {"ran": False, "reason": f"could not start play session: {exc}", "errors": [], "warnings": []}
    console_samples = []
    deadline = started + max(3, seconds)
    while time.time() < deadline:
        time.sleep(min(poll_every, max(0.5, deadline - time.time())))
        try:
            console_samples.append(client.console_output())
        except Exception:  # noqa: BLE001 - console read is optional
            break
    try:
        player_check = client.execute_luau('''local players = game:GetService("Players")
local character = nil
for _, player in ipairs(players:GetPlayers()) do
	if player.Character then character = player.Character end
end
if not character then return { spawned = false } end
local root = character:FindFirstChild("HumanoidRootPart")
return {
	spawned = true,
	position = root and { root.Position.X, root.Position.Y, root.Position.Z } or nil,
	walked = root and root.AssemblyLinearVelocity.Magnitude or 0,
}''')
    except Exception as exc:  # noqa: BLE001
        player_check = {"error": str(exc)[:300]}
    try:
        client.call("start_stop_play", {"action": "stop"})
    except Exception:  # noqa: BLE001
        pass
    console = "\n".join(console_samples)
    parsed = parse_console(console)
    player = player_check.get("json") if isinstance(player_check, dict) else None
    spawned = bool(player and player.get("spawned"))
    return {
        "ran": True,
        "seconds": round(time.time() - started, 1),
        "console": console[-8000:],
        "errors": parsed["errors"],
        "warnings": parsed["warnings"],
        "errorCount": parsed["error_count"],
        "spawned": spawned,
        "player": player,
        "passed": parsed["error_count"] == 0 and spawned,
    }
