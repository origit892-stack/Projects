"""BloxUI engine -- professional game UI as a BloxUI blueprint + hook scripts.

BloxUI (the BloxMaps UI Designer) builds real, animated, mobile-aware Roblox UI at runtime
from a **blueprint** (a JSON StringValue in ``ReplicatedStorage.BloxUI_Blueprints.<Name>``) plus
a proprietary ``BloxUI`` runtime ModuleScript, a ``BloxUI_BlueprintLoader`` and two hook scripts.
See docs.bloxmaps.com/ui/how-it-works and /ui/scripting.

This engine does what we *can* own without the proprietary runtime binary:

1. **Author the blueprint JSON** from the game's design + art direction -- screens, tabs, HUD,
   currencies, shop sections and items, colours, fonts, sounds -- using the documented field
   names (screens, elements, ``action`` kinds Open/Purchase/GamePass/Remote/Event/Notify/None,
   currencies, sections). The BloxUI loader *repairs* missing values with safe defaults, so a
   well-formed blueprint installs cleanly.
2. **Generate the two hook scripts** (``<Name>_UIHooks`` LocalScript, ``<Name>_ServerHooks``
   server Script) with a ready handler stub for every button/event/remote/product the design
   fires -- exactly the shape BloxUI expects.
3. **Install into Studio** through the MCP (drop the blueprint StringValue + hooks into place);
   the ``BloxUI`` runtime itself ships from a BloxUI export (Send-to-Studio / .rbxmx), which the
   engine reports honestly when it is not present.

The engine never pretends the runtime is installed; ``available()`` and the install report state
it plainly.
"""
from __future__ import annotations

import json
from typing import Any

from .base import BaseEngine, EngineResult

# action kinds documented by BloxUI (docs.bloxmaps.com/ui/scripting)
ACTION_KINDS = ("Open", "Close", "Toggle", "Purchase", "GamePass", "Remote", "Event", "Notify", "None")


class BloxUIEngine(BaseEngine):
    name = "bloxui"
    label = "BloxUI (UI Designer)"
    purpose = "Game design -> professional UI blueprint + hook scripts (HUD, shop, inventory, settings...)"

    # -- status ----------------------------------------------------------------------
    def available(self) -> dict:
        return {"engine": self.name, "live": True,
                "reason": "Blueprint + hook generator is always available. The BloxUI *runtime* "
                          "ModuleScript ships from a BloxUI export (Send-to-Studio / .rbxmx); "
                          "installation into Studio needs the Studio MCP."}

    # -- blueprint authoring ---------------------------------------------------------
    def build_blueprint(self, name: str, title: str, *, colors: dict | None = None,
                        panel: str = "Dark", fonts: dict | None = None,
                        currencies: list[dict] | None = None, screens: list[dict] | None = None,
                        hud: list[dict] | None = None, shop: list[dict] | None = None,
                        sounds: dict | None = None) -> dict:
        colors = colors or {"primary": "#3b82f6", "accent": "#f59e0b", "background": "#0f172a",
                            "text": "#f8fafc", "surface": "#1e293b", "success": "#22c55e"}
        blueprint: dict[str, Any] = {
            "schema": "bloxui", "version": 1, "name": name, "title": title,
            "panel": panel, "colors": colors,
            "fonts": fonts or {"headings": "Fredoka One", "body": "Montserrat", "ui": "Montserrat"},
            "currencies": currencies or [],
            "hud": hud or [],
            "screens": screens or [],
            "shop": shop or [],
            "sounds": sounds or {"click": "", "open": "", "success": "", "error": ""},
            "mobile": {"scale": 1.0, "safeArea": True, "touchTargets": 44},
        }
        return blueprint

    def blueprint_to_lua_string(self, blueprint: dict) -> str:
        """The blueprint as a StringValue payload (JSON text)."""
        return json.dumps(blueprint, ensure_ascii=False, indent=2)

    # -- hook scripts ----------------------------------------------------------------
    def generate_hooks(self, name: str, design: dict | None = None) -> dict:
        """Return {ui_hooks, server_hooks, blueprint_name} as ready-to-install Luau sources."""
        design = design or {}
        events = _collect_events(design)
        ui_hooks = _render_ui_hooks(name, events)
        server_hooks = _render_server_hooks(name, events)
        return {"blueprint_name": name, "ui_hooks": ui_hooks, "server_hooks": server_hooks,
                "events": events}

    # -- install into Studio ---------------------------------------------------------
    def install(self, studio_client, name: str, blueprint: dict) -> EngineResult:
        import time
        started = time.time()
        hooks = self.generate_hooks(name)
        code = _install_code(name, self.blueprint_to_lua_string(blueprint), hooks["ui_hooks"], hooks["server_hooks"])
        try:
            result = studio_client.execute_luau(code, timeout=120)
            payload = result.get("json") or _extract(result.get("text", "")) or {"text": result.get("text", "")}
            if result.get("isError") or not payload.get("ok", False):
                return EngineResult(self.name, "error",
                                    error=f"install failed: {str(payload)[:300]}",
                                    seconds=time.time() - started)
            notes = ["blueprint StringValue + UI/Server hooks installed via Studio MCP"]
            runtime = payload.get("runtime_present")
            if runtime is False:
                notes.append("BloxUI runtime ModuleScript NOT present yet -- run a BloxUI "
                             "Send-to-Studio export (or drop the .rbxmx) so the UI can build at Play.")
            elif runtime:
                notes.append("BloxUI runtime present")
            return EngineResult(self.name, "ok", payload=payload, notes=notes, seconds=time.time() - started)
        except Exception as exc:  # noqa: BLE001
            return EngineResult(self.name, "error", error=str(exc)[:400], seconds=time.time() - started)

    # -- build entry point (used by the orchestrator) --------------------------------
    def build(self, *args, **kwargs) -> EngineResult:
        """Build a blueprint + hooks from a design dict. ``install`` is called separately."""
        import time
        started = time.time()
        design = kwargs.get("design") or {}
        name = kwargs.get("name") or _slug(kwargs.get("title") or design.get("title") or "GameUI")
        blueprint = self.build_blueprint(
            name, kwargs.get("title") or design.get("title") or name,
            colors=kwargs.get("colors"), panel=kwargs.get("panel") or "Dark",
            fonts=kwargs.get("fonts"), currencies=kwargs.get("currencies"),
            screens=kwargs.get("screens"), hud=kwargs.get("hud"), shop=kwargs.get("shop"))
        hooks = self.generate_hooks(name, design)
        return EngineResult(self.name, "ok",
                            payload={"blueprint": blueprint, "hooks": {
                                "ui_hooks": hooks["ui_hooks"], "server_hooks": hooks["server_hooks"],
                                "events": hooks["events"], "blueprint_name": name}},
                            notes=["blueprint + hooks generated (not yet installed)"],
                            seconds=time.time() - started)


# --------------------------------------------------------------------------- helpers
def _slug(text: str) -> str:
    import re
    cleaned = re.sub(r"[^A-Za-z0-9]+", "", str(text))
    return cleaned or "GameUI"


def _collect_events(design: dict) -> list[dict]:
    """Gather every event/remote the UI will fire so the hooks have a stub for each."""
    events: list[dict] = []
    seen: set[str] = set()
    for screen in (design.get("screens") or []):
        for element in (screen.get("elements") or []):
            action = element.get("action") or {}
            kind = action.get("kind", "None")
            if kind in ("Event", "Remote"):
                name = action.get("name") or element.get("id")
                if name and name not in seen:
                    seen.add(name)
                    events.append({"id": element.get("id", name), "name": name,
                                   "kind": kind, "screen": screen.get("id"),
                                   "payload": action.get("payload")})
    return events


def _render_ui_hooks(name: str, events: list[dict]) -> str:
    lines = [
        f'-- <{name}_UIHooks>  LocalScript in StarterPlayer > StarterPlayerScripts',
        '-- Generated by Idea2World 7.0 (BloxUI engine). Fill in the handlers with your game code.',
        'local ReplicatedStorage = game:GetService("ReplicatedStorage")',
        'local UI = require(ReplicatedStorage:WaitForChild("BloxUI"))',
        f'local ui = UI.Blueprint.waitFor("{name}", 30)',
        f'if ui == nil then warn("Idea2World: UI "{name}" was not built; is BloxUI_BlueprintLoader present?") return end',
        '',
        '-- Screen open/close',
        'ui:on("ScreenOpened", function(context) print("[I2W] opened", context.screen) end)',
        'ui:on("ScreenClosed", function(context) print("[I2W] closed", context.screen) end)',
        '',
    ]
    for event in events:
        lines.append(f'ui:on("{event["name"]}", function(context)')
        lines.append(f'\t-- {event["kind"]} from {event["screen"]}/{event["id"]}; context.id, context.payload')
        lines.append(f'\tprint("[I2W] {event["name"]}", context.id, context.payload)')
        lines.append('end)')
    if not events:
        lines.append('-- (no Event/Remote buttons in this design yet)')
    return "\n".join(lines)


def _render_server_hooks(name: str, events: list[dict]) -> str:
    lines = [
        f'-- <{name}_ServerHooks>  Script in ServerScriptService (enable it)',
        '-- Generated by Idea2World 7.0 (BloxUI engine). Validate every value a client sends.',
        'local ReplicatedStorage = game:GetService("ReplicatedStorage")',
        'local UI = require(ReplicatedStorage:WaitForChild("BloxUI"))',
        '',
    ]
    for event in events:
        if event["kind"] != "Remote":
            continue
        lines.append(f'UI.Server.on("{event["name"]}", function(player, elementId, payload)')
        lines.append('\t-- validate payload here, then grant the reward; return true on success')
        lines.append(f'\tprint("[I2W:server] {event["name"]}", player.Name, elementId, payload)')
        lines.append('\treturn false')
        lines.append('end)')
    lines += [
        '',
        '-- Server products (add real Developer Product ids in the blueprint, then deliver here)',
        '-- UI.Server.onReceipt(<productId>, function(player) return true end)',
        '',
        'UI.Server.start({ SaveData = true, SaveSettings = true })',
    ]
    return "\n".join(lines)


def _install_code(name: str, blueprint_json: str, ui_hooks: str, server_hooks: str) -> str:
    # Escape for a Luau long string; the blueprint JSON becomes a StringValue payload.
    def ls(text: str) -> str:
        return " [[" + text.replace("]]", "])[").strip("\n") + "]] "
    return "\n".join([
        'local ReplicatedStorage = game:GetService("ReplicatedStorage")',
        'local SSP = game:GetService("ServerScriptService")',
        'local StarterPlayer = game:GetService("StarterPlayer")',
        'local SSP_scripts = StarterPlayer:WaitForChild("StarterPlayerScripts")',
        f'local runtimePresent = ReplicatedStorage:FindFirstChild("BloxUI") ~= nil',
        'local blueprints = ReplicatedStorage:FindFirstChild("BloxUI_Blueprints")',
        'if not blueprints then blueprints = Instance.new("Folder"); blueprints.Name = "BloxUI_Blueprints"; blueprints.Parent = ReplicatedStorage end',
        f'local sv = Instance.new("StringValue"); sv.Name = "{name}"',
        f'sv.Value = {ls(blueprint_json)}; sv.Parent = blueprints',
        f'local uiH = Instance.new("LocalScript"); uiH.Name = "{name}_UIHooks"',
        f'uiH.Source = {ls(ui_hooks)}; uiH.Parent = SSP_scripts',
        f'local srvH = Instance.new("Script"); srvH.Name = "{name}_ServerHooks"',
        f'srvH.Source = {ls(server_hooks)}; srvH.Enabled = true; srvH.Parent = SSP',
        'return { ok = true, runtime_present = runtimePresent }',
    ])


def _extract(text: str) -> dict | None:
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None
    return None
