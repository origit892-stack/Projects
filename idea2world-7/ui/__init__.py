"""Idea2World 7.0 UI Studio.

6.0 had no UI at all -- the world was geometry. 7.0 adds a UI department that turns the game
design + art direction into a real, working Roblox UI in one of two backends:

* **native** -- a self-contained UI framework we fully own: a ScreenGui with a loading screen,
  main menu, HUD (cash / XP / level / health), shop (server-validated purchases), inventory,
  settings, and a notification system, built with TweenService animations and a mobile-safe
  scale. Always available, always verifiable (luau-compile + the DataModel simulator).
* **bloxui** -- a BloxUI blueprint + hook scripts (the user's chosen UI tool) that the BloxUI
  runtime builds at Play. See ``engines/bloxui.py``.

Both backends are driven from the same UI spec, so the design decision is data, not code.
"""
from __future__ import annotations
