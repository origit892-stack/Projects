"""Engine registry -- which of the user's tools are actually live, and how to reach them.

The orchestrator asks the registry for the right engine per concern (world / assets / ui) and
for an honest status list to show in the Toolchain panel. The registry never enables a tool that
has no key / no Studio session; it reports the reason and names the fallback.
"""
from __future__ import annotations

import os
from pathlib import Path

from .base import BaseEngine, EngineResult, HttpClient
from .bloxmaps import BloxMapsEngine
from .bloxui import BloxUIEngine
from .meshy import MeshyEngine


class EngineRegistry:
    def __init__(self, studio_client=None):
        self.studio_client = studio_client
        self.bloxmaps = BloxMapsEngine(studio_client=studio_client)
        self.meshy = MeshyEngine()
        self.bloxui = BloxUIEngine()
        # local procedural builder is 6.0's always-available world engine (not a key-gated tool)
        self.local = {"engine": "local_procedural", "live": True,
                      "reason": "Built into Idea2World (deterministic terrain, biomes, shaped "
                                "recipes, 18-file Luau). Always available; no key needed."}
        # tools without a public API -> manual assist only (honest)
        self.manual = [
            {"engine": "odyssey", "live": False,
             "reason": "Odyssey Terrain Editor is a Roblox Store plugin with no public API -- "
                       "manual assist: open it in Studio and shape the terrain; Idea2World's "
                       "local terrain can then be re-read."},
            {"engine": "better_ui_editor", "live": False,
             "reason": "Better UI Editor is a Roblox Store plugin with no public API -- manual "
                       "assist for precise UI alignment after the BloxUI/native UI is installed."},
        ]

    def status(self) -> list[dict]:
        order = [self.local, self.bloxmaps.available(), self.bloxui.available(), self.meshy.available()]
        return order + self.manual

    def world_engine(self, preferred: str | None) -> str:
        """Return the world-builder to use: bloxmaps if it's live and preferred, else local."""
        if preferred == "bloxmaps" and self.bloxmaps.available()["live"]:
            return "bloxmaps"
        if preferred in (None, "auto", "local", "local_procedural"):
            return "local_procedural"
        if preferred == "bloxmaps":
            return "local_procedural"  # requested but not configured -> honest fallback
        return "local_procedural"

    def ui_engine(self, preferred: str | None) -> str:
        """bloxui (blueprint+hooks) or native (self-contained Roblox UI). Both are available."""
        if preferred in (None, "auto"):
            return "native" if self.studio_client is None else "bloxui"
        return preferred if preferred in ("native", "bloxui") else "native"

    def asset_engine(self, preferred: str | None) -> str:
        if preferred == "meshy" and self.meshy.available()["live"]:
            return "meshy"
        return "recipes"  # layered part recipes, always available

    def get(self, name: str) -> BaseEngine | None:
        return {"bloxmaps": self.bloxmaps, "meshy": self.meshy, "bloxui": self.bloxui}.get(name)

    def describe(self) -> dict:
        return {"status": self.status(), "engines": {"world": self.world_engine(None),
                                                     "ui": self.ui_engine(None),
                                                     "assets": self.asset_engine(None)}}
