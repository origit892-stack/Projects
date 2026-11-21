"""UI spec builder -- turns a game's design + art direction into a backend-agnostic UI spec.

The spec is data: which screens the game needs, the HUD readouts, the shop catalogue and prices,
the currency and the colours/fonts (pulled from the art direction). Both the native generator and
the BloxUI engine consume it, so "what the UI is" is decided once, in one place.
"""
from __future__ import annotations

import re
from typing import Any

# screen -> the elements it carries, keyed by element id (stable so hooks can reference them)
SCREEN_CATALOG: dict[str, list[dict]] = {
    "loading": [
        {"id": "logo", "kind": "label", "text": "{title}", "center": True},
        {"id": "progress", "kind": "progressbar", "max": 100},
        {"id": "tip", "kind": "label", "text": "Tip: the world is building itself.", "bottom": True},
    ],
    "main_menu": [
        {"id": "title", "kind": "label", "text": "{title}", "big": True},
        {"id": "playButton", "kind": "button", "text": "Play", "action": {"kind": "Event", "name": "Play"}},
        {"id": "shopButton", "kind": "button", "text": "Shop", "action": {"kind": "Open", "target": "shop"}},
        {"id": "settingsButton", "kind": "button", "text": "Settings", "action": {"kind": "Open", "target": "settings"}},
        {"id": "credits", "kind": "label", "text": "Idea2World", "bottom": True},
    ],
    "shop": [
        {"id": "backButton", "kind": "button", "text": "Back", "action": {"kind": "Close"}},
        {"id": "cashLabel", "kind": "label", "text": "Cash: {cash}"},
        {"id": "shopList", "kind": "list", "items": "{shop}"},
    ],
    "inventory": [
        {"id": "backButton", "kind": "button", "text": "Back", "action": {"kind": "Close"}},
        {"id": "inventoryList", "kind": "list", "items": "{inventory}"},
    ],
    "settings": [
        {"id": "backButton", "kind": "button", "text": "Back", "action": {"kind": "Close"}},
        {"id": "sfxToggle", "kind": "toggle", "text": "Sound FX", "default": True},
        {"id": "musicToggle", "kind": "toggle", "text": "Music", "default": True},
        {"id": "qualityToggle", "kind": "toggle", "text": "High Quality", "default": True},
        {"id": "resetButton", "kind": "button", "text": "Reset", "action": {"kind": "Event", "name": "ResetSettings"}},
    ],
}

# HUD readouts and their data keys
HUD_ELEMENTS: list[dict] = [
    {"id": "cashHud", "kind": "stat", "label": "Cash", "data": "cash", "icon": "$"},
    {"id": "xpHud", "kind": "stat", "label": "XP", "data": "xp", "icon": "*"},
    {"id": "levelHud", "kind": "stat", "label": "Level", "data": "level", "icon": "#"},
    {"id": "healthHud", "kind": "healthbar", "data": "health", "max": 100},
    {"id": "openShop", "kind": "button", "text": "Shop", "action": {"kind": "Open", "target": "shop"}},
    {"id": "openInventory", "kind": "button", "text": "Bag", "action": {"kind": "Open", "target": "inventory"}},
]


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "", str(text))
    return cleaned or "GameUI"


def colors_from_art(art: dict | None) -> dict:
    palette = (art or {}).get("palette") or {}
    return {
        "primary": palette.get("accent") or "#3b82f6",
        "accent": palette.get("highlight") or "#f59e0b",
        "background": palette.get("sky", {}).get("top") or "#0f172a",
        "surface": palette.get("field") or "#1e293b",
        "text": "#f8fafc",
        "success": "#22c55e",
        "danger": "#ef4444",
    }


def build_ui_spec(design: dict, art: dict | None = None, *, title: str = "", name: str = "",
                  screens: list[str] | None = None, shop_items: list[dict] | None = None,
                  currency: dict | None = None) -> dict:
    """Assemble the full UI spec for a game."""
    title = title or design.get("title") or (name or "Game")
    name = name or _slug(title)
    genre = design.get("genre", "simulator")
    wanted = screens or _default_screens(genre)
    spec: dict[str, Any] = {
        "name": name,
        "title": title,
        "genre": genre,
        "colors": colors_from_art(art),
        "fonts": {"headings": "Fredoka One", "body": "Montserrat", "ui": "Montserrat"},
        "panel": "Dark",
        "currency": currency or {"id": "cash", "label": "Cash", "icon": "$", "start": 0},
        "hud": HUD_ELEMENTS,
        "screens": [{ "id": s, "elements": SCREEN_CATALOG.get(s, []) } for s in wanted],
        "shop": shop_items or _default_shop(genre),
        "events": _collect_events(wanted),
    }
    return spec


def _default_screens(genre: str) -> list[str]:
    base = ["loading", "main_menu", "shop", "inventory", "settings"]
    return base


def _default_shop(genre: str) -> list[dict]:
    base = [
        {"id": "boost_double", "name": "2x Boost (10 min)", "price": 250, "icon": "x2"},
        {"id": "starter_pack", "name": "Starter Pack", "price": 500, "icon": "box"},
        {"id": "skin_cool", "name": "Cool Skin", "price": 1200, "icon": "skin"},
        {"id": "pass_vip", "name": "VIP Pass", "price": 3000, "icon": "crown", "kind": "pass"},
    ]
    return base


def _collect_events(screen_ids: list[str]) -> list[dict]:
    events: list[dict] = []
    seen: set[str] = set()
    for screen_id in screen_ids:
        for element in SCREEN_CATALOG.get(screen_id, []):
            action = element.get("action") or {}
            kind = action.get("kind")
            if kind in ("Event", "Remote") and action.get("name") and action["name"] not in seen:
                seen.add(action["name"])
                events.append({"id": element.get("id"), "name": action["name"], "kind": kind,
                               "screen": screen_id})
    return events


def bloxui_screens(spec: dict) -> list[dict]:
    """Map a UI spec to the screen shape the BloxUI blueprint expects."""
    screens: list[dict] = []
    for screen in spec["screens"]:
        screens.append({
            "id": screen["id"],
            "title": screen["id"].replace("_", " ").title(),
            "elements": screen["elements"],
        })
    return screens


def bloxui_currencies(spec: dict) -> list[dict]:
    cur = spec["currency"]
    return [{"id": cur["id"], "label": cur["label"], "icon": cur.get("icon", "$"),
             "start": cur.get("start", 0)}]
