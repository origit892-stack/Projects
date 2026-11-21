"""Design-principle knowledge base for successful Roblox experiences.

This stores *observable design principles* (scale, density, palette strategy, path structure,
onboarding) extracted from public game descriptions and screenshots. It never stores, copies or
reconstructs maps, models, textures, code or other protected assets. Every field is written as a
transferable rule that the planner can apply to a brand-new world.
"""
from __future__ import annotations

from typing import Iterable

# Player character is ~5 studs tall. All scale targets below are expressed relative to it so the
# planner can keep buildings and props believable instead of accidentally building giant boxes.
PLAYER_HEIGHT_STUDS = 5.0

REFERENCES: dict[str, dict] = {
    "grow_a_garden": {
        "label": "Cozy growth & collection (Grow a Garden-like)",
        "genre_tags": ["collection_garden", "throw_collect_sim", "cozy", "tycoon"],
        "keywords": ["garden", "grow", "plant", "farm", "pet", "collect", "גינה", "לגדל", "לאסוף"],
        "density": {"props_per_100m2": 2.4, "path_share": 0.16, "open_share": 0.30},
        "scale": {"building_height": "4-7x player", "prop_height": "0.6-2.2x player",
                  "plot_width": "14-22 studs", "walkway_width": "8-12 studs"},
        "palette_strategy": "saturated foliage greens as the field, warm wooden structures as the "
                            "mid-tone, a single bright accent reserved for rewards and rarity",
        "composition": "personal plots arranged around one shared social plaza, expansion rings that "
                       "always show the next unlock, long sightline to the rarest plant/flower",
        "lighting": "bright late-morning sun, soft ambient, gentle god-rays; almost no darkness",
        "ui": "inventory bar at the bottom, plot status above the plot in-world, collection grid",
        "principles": [
            "First harvest happens within 20 seconds of joining.",
            "Every reward is visible in the world before it is explained in UI.",
            "Rarity reads through color + silhouette + particle, never color alone.",
            "Plots are personal but always overlook the shared plaza so other players stay visible.",
        ],
    },
    "adopt_me": {
        "label": "Social roleplay & home ownership (Adopt Me-like)",
        "genre_tags": ["social_roleplay", "collection_garden", "general_adventure"],
        "keywords": ["roleplay", "house", "home", "city", "school", "town", "עיר", "בית", "תפקידים"],
        "density": {"props_per_100m2": 1.8, "path_share": 0.22, "open_share": 0.34},
        "scale": {"building_height": "5-9x player", "door_width": "1.6-2.2x player",
                  "plaza_width": "40-70 studs", "walkway_width": "10-16 studs"},
        "palette_strategy": "pastel mid-tones for homes, one saturated accent per district so players "
                            "can describe where they are, natural greens between districts",
        "composition": "compact walkable districts joined by a central plaza; each district has one "
                       "recognisable silhouette (clock tower, bridge, lighthouse)",
        "lighting": "golden-hour warmth with cool shadows; interiors need readable fill light",
        "ui": "minimal HUD, large emote and action buttons, location labels",
        "principles": [
            "Districts are compact enough to walk across in under 40 seconds.",
            "Meeting points sit on the path between districts, not off to the side.",
            "Homes are visible from the main path so ownership is social proof.",
            "Decoration density is highest at eye level, lowest on roofs and far hills.",
        ],
    },
    "fisch": {
        "label": "Fishing & exploration progression (Fisch-like)",
        "genre_tags": ["survival_exploration", "collection_garden", "general_adventure"],
        "keywords": ["fish", "fishing", "ocean", "island", "sea", "דיג", "ים", "אי"],
        "density": {"props_per_100m2": 1.5, "path_share": 0.12, "open_share": 0.42},
        "scale": {"cliff_height": "8-20x player", "dock_length": "30-60 studs",
                  "island_spacing": "1.2-2.0 island diameters", "walkway_width": "8-14 studs"},
        "palette_strategy": "deep blue-teal water as the dominant field, warm sand/rock mid-tones, "
                            "one luminous accent for rare catches and portals",
        "composition": "layered islands with strong vertical landmarks; the horizon must always hold "
                       "a destination silhouette so exploration feels authored",
        "lighting": "clear high sun with strong water specular, cool haze on distant islands",
        "ui": "minimal, contextual prompts near the water, rarity reveal on catch",
        "principles": [
            "A destination silhouette is visible from every island.",
            "Water edges are readable: shallow, deep and blocked zones look different.",
            "Rare content sits behind a visible landmark, never behind an invisible wall.",
            "Long routes need rest points every 8-12 seconds of travel.",
        ],
    },
    "blox_fruits": {
        "label": "Action-adventure traversal (Blox Fruits-like)",
        "genre_tags": ["competitive_action", "survival_exploration", "general_adventure"],
        "keywords": ["battle", "fight", "fruit", "pirate", "power", "קרב", "כוח", "פיראטים"],
        "density": {"props_per_100m2": 1.2, "path_share": 0.10, "open_share": 0.46},
        "scale": {"landmark_height": "20-60x player", "arena_width": "80-140 studs",
                  "gate_width": "12-20 studs", "walkway_width": "10-18 studs"},
        "palette_strategy": "biome-coded saturation: each island owns one hue family, accents reserved "
                            "for interactables and danger telegraphs",
        "composition": "island network with a dominant central structure, deliberately wide combat "
                       "arenas, cover objects that never block the main sightline",
        "lighting": "dramatic key light, colored rim light per biome, controlled bloom on abilities",
        "ui": "cooldown-first ability bar, compact health, clear objective pin",
        "principles": [
            "Sightlines in combat areas stay clear at player height.",
            "Every biome shift is announced visually before it is announced in UI.",
            "Vertical traversal (cliffs, towers) is rewarded with a view of the next zone.",
            "Landmarks are oversized so navigation works without a minimap.",
        ],
    },
    "general_adventure": {
        "label": "Discovery & exploration baseline",
        "genre_tags": ["general_adventure", "*"],
        "keywords": ["*"],
        "density": {"props_per_100m2": 1.6, "path_share": 0.14, "open_share": 0.38},
        "scale": {"building_height": "4-8x player", "prop_height": "0.5-2.0x player",
                  "walkway_width": "10-16 studs", "poi_spacing": "180-320 studs"},
        "palette_strategy": "one dominant field color, two supporting mid-tones, one accent used only "
                            "for interactables and the current objective",
        "composition": "spawn hub -> strong focal landmark -> 3-5 distinct districts -> visible next goal",
        "lighting": "readable key light with soft fill, atmosphere used for depth not obstruction",
        "ui": "objective, progress, inventory, next unlock",
        "principles": [
            "First satisfying action within 20 seconds of spawn.",
            "The current objective is visible in the world, not only in UI.",
            "Every path leads somewhere intentional; no corridor ends in a wall.",
            "Reuse 6-12 hero asset variants with rotation, scale and color variation instead of "
            "spawning hundreds of unique meshes.",
        ],
    },
}

# Visual language library. These are complete, self-consistent art directions the Art Director can
# adopt and then bend toward a specific idea.
STYLE_LIBRARY: dict[str, dict] = {
    "stylized_low_poly": {
        "label": "Stylized Low Poly",
        "geometry": "clean faceted silhouettes, layered shapes, deliberate negative space",
        "materials": {"ground": "Grass", "rock": "Rock", "wood": "Wood", "stone": "Slate",
                      "metal": "Metal", "water": "Water", "accent": "Neon"},
        "palette": ["#4f7a45", "#7fae5c", "#b9a06b", "#6c8fa6", "#e0c98a", "#8a6a4a"],
        "lighting": {"clock_time": 15.2, "brightness": 2.2, "ambient": [96, 104, 120],
                     "outdoor_ambient": 0.55, "fog_density": 0.18, "exposure": 0.15},
        "detail_bias": "silhouette-first, low triangle counts, hand-placed clusters",
        "avoid": ["photoreal textures", "noisy small props at distance", "flat single-color planes"],
        "target_part_ratio": 0.55,
    },
    "fantasy_cinematic": {
        "label": "Fantasy Cinematic",
        "geometry": "monumental arches, layered ruins, organic rock and root silhouettes",
        "materials": {"ground": "Ground", "rock": "Rock", "wood": "WoodPlanks", "stone": "Cobblestone",
                      "metal": "CorrodedMetal", "water": "Water", "accent": "Neon"},
        "palette": ["#3b4a3a", "#6f7f52", "#8d8069", "#5c4b63", "#f0c674", "#7fd6c1"],
        "lighting": {"clock_time": 17.4, "brightness": 1.9, "ambient": [70, 66, 88],
                     "outdoor_ambient": 0.4, "fog_density": 0.3, "exposure": 0.25},
        "detail_bias": "large forms with selective ornate detailing near the player",
        "avoid": ["clean sci-fi panels", "flat daylight", "identical repeated towers"],
        "target_part_ratio": 0.5,
    },
    "cosmic_art": {
        "label": "Cosmic Art Direction",
        "geometry": "floating masses, orbital rings, asymmetric crystal growth",
        "materials": {"ground": "Ground", "rock": "Basalt", "wood": "Wood", "stone": "Slate",
                      "metal": "Metal", "water": "Glass", "accent": "Neon"},
        "palette": ["#1b1630", "#2f2a55", "#4b3f86", "#7c5cff", "#43d9d0", "#d9c9ff"],
        "lighting": {"clock_time": 0.3, "brightness": 1.2, "ambient": [48, 42, 92],
                     "outdoor_ambient": 0.25, "fog_density": 0.4, "exposure": 0.35},
        "detail_bias": "sparse but luminous; emissive accents carry the composition",
        "avoid": ["bright daylight greens", "clutter at ground level", "warm brown wood tones"],
        "target_part_ratio": 0.45,
    },
    "sci_fi_clean": {
        "label": "Clean Sci-Fi",
        "geometry": "modular panels, pylons, rings, engineered proportions",
        "materials": {"ground": "Concrete", "rock": "Slate", "wood": "Metal", "stone": "Concrete",
                      "metal": "Metal", "water": "Glass", "accent": "Neon"},
        "palette": ["#2b3138", "#5b6a76", "#a8b6c0", "#22d3ee", "#f2f7fa", "#7c8794"],
        "lighting": {"clock_time": 13.0, "brightness": 2.0, "ambient": [88, 96, 108],
                     "outdoor_ambient": 0.5, "fog_density": 0.12, "exposure": 0.1},
        "detail_bias": "precise repetition and panel lines, few but strong accents",
        "avoid": ["organic clutter", "warm rustic materials", "asymmetric mess"],
        "target_part_ratio": 0.5,
    },
    "stud": {
        "label": "Classic Roblox Stud",
        "geometry": "chunky modular forms, readable block language used deliberately",
        "materials": {"ground": "Grass", "rock": "Slate", "wood": "Wood", "stone": "Brick",
                      "metal": "Metal", "water": "Water", "accent": "Neon"},
        "palette": ["#3f9b3f", "#8bd44b", "#c9a227", "#3d7fc1", "#f2f2f2", "#b4553f"],
        "lighting": {"clock_time": 14.0, "brightness": 2.4, "ambient": [110, 112, 126],
                     "outdoor_ambient": 0.65, "fog_density": 0.1, "exposure": 0.05},
        "detail_bias": "playful chunky props, strong color blocking",
        "avoid": ["photorealism", "thin fragile geometry", "muddy palettes"],
        "target_part_ratio": 0.65,
    },
    "natural_realism": {
        "label": "Natural Realism",
        "geometry": "irregular organic terrain, dense layered vegetation, believable weathering",
        "materials": {"ground": "Ground", "rock": "Rock", "wood": "Wood", "stone": "Slate",
                      "metal": "CorrodedMetal", "water": "Water", "accent": "Neon"},
        "palette": ["#38502f", "#5f7a44", "#8a8a6e", "#4c6b74", "#b9b39a", "#5a4635"],
        "lighting": {"clock_time": 16.1, "brightness": 2.0, "ambient": [88, 96, 104],
                     "outdoor_ambient": 0.5, "fog_density": 0.22, "exposure": 0.12},
        "detail_bias": "high variation in scale, rotation and clustering; avoid visible tiling",
        "avoid": ["perfectly straight rows", "single tree repeated", "plastic flat color"],
        "target_part_ratio": 0.4,
    },
}

THEME_ACCENTS: dict[str, dict] = {
    "natural": {"accent": "#e0c98a", "props": ["stone_shrine", "fallen_log", "rock_garden", "watch_post"],
                "vfx": ["fireflies", "pollen", "water_spray"]},
    "cosmic": {"accent": "#8b5cf6", "props": ["floating_obelisk", "star_orb", "crystal_cluster", "rift_arch"],
               "vfx": ["stardust", "nebula_mist", "arcane_rings", "meteor_sparks"]},
    "sci_fi": {"accent": "#22d3ee", "props": ["antenna_array", "holo_pylon", "reactor_core", "drone_dock"],
               "vfx": ["hologram_beam", "energy_arcs", "thruster_plume", "scan_pulse"]},
    "fantasy": {"accent": "#f0c674", "props": ["rune_stone", "crystal_cluster", "ancient_shrine", "lantern_post"],
                "vfx": ["fairy_motes", "rune_glow", "magic_sparks", "soft_mist"]},
    "crystal": {"accent": "#67e8f9", "props": ["crystal_cluster", "geode_arch", "prism_spire"],
                "vfx": ["crystal_shimmer", "glitter", "light_rays"]},
    "steampunk": {"accent": "#d6a45d", "props": ["gear_stack", "brass_tower", "pipe_organ", "airship_mooring"],
                  "vfx": ["steam_burst", "pressure_vent", "sparks"]},
}


def match_reference(text: str, genre_profile: str = "") -> dict:
    """Pick the reference whose principles best explain this idea."""
    low = (text or "").lower()
    best_key, best_score = "general_adventure", 0.0
    for key, ref in REFERENCES.items():
        score = 0.0
        if genre_profile and genre_profile in ref["genre_tags"]:
            score += 1.5
        for kw in ref["keywords"]:
            if kw == "*":
                continue
            if kw in low:
                score += 1.0
        if score > best_score:
            best_key, best_score = key, score
    return dict(REFERENCES[best_key], id=best_key)


def reference_board(genre_profile: str, limit: int = 4) -> list[dict]:
    """Return a compact principles board for a genre, best match first."""
    scored = []
    for key, ref in REFERENCES.items():
        score = 2 if genre_profile in ref["genre_tags"] else 0
        scored.append((score, key, ref))
    scored.sort(key=lambda item: -item[0])
    return [{"id": k, "label": r["label"], "density": r["density"], "scale": r["scale"],
             "palette_strategy": r["palette_strategy"], "composition": r["composition"],
             "lighting": r["lighting"], "principles": r["principles"]}
            for _, k, r in scored[:limit]]


def principles_for(*refs) -> list[str]:
    """Accepts either several reference dicts or a single list of them."""
    if len(refs) == 1 and isinstance(refs[0], (list, tuple)):
        refs = tuple(refs[0])
    seen, out = set(), []
    for ref in refs:
        for p in (ref.get("principles") or []):
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out
