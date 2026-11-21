"""Art-direction synthesis: turns a free-form idea into a testable visual language.

The output is not decoration -- every field here is consumed later by the Luau generator, the
asset planner and the visual critic (which scores the built map against the same values).
"""
from __future__ import annotations

from .reference_library import STYLE_LIBRARY, THEME_ACCENTS, match_reference, principles_for

STYLE_KEYWORDS = {
    "stud": ["stud", "studs", "classic roblox", "classic", "בלוקים"],
    "cosmic_art": ["cosmic", "space", "galaxy", "nebula", "star", "celestial", "חלל", "קוסמי", "גלקסיה", "כוכבים"],
    "sci_fi_clean": ["sci-fi", "scifi", "futuristic", "cyber", "neon city", "עתידני", "סייבר"],
    "fantasy_cinematic": ["fantasy", "magic", "magical", "enchanted", "wizard", "medieval", "פנטזיה", "קסום", "אגדי"],
    "natural_realism": ["realistic", "realism", "photoreal", "ריאליסטי", "טבעי"],
}

MOOD_BY_STYLE = {
    "stylized_low_poly": "inviting, readable adventure with soft contrast",
    "fantasy_cinematic": "mythic and awe-driven, warm light against cool shadow",
    "cosmic_art": "quiet cosmic wonder with a luminous focal point",
    "sci_fi_clean": "precise, calm and technical with sparse neon accents",
    "stud": "playful, high-energy and instantly legible",
    "natural_realism": "grounded, textured and atmospheric",
}

# Six named palette roles keep every consumer (Lua, UI, critic) talking about the same colors.
PALETTE_ROLES = ["field", "field_alt", "structure", "structure_alt", "accent", "highlight"]


def choose_style(idea: str, requested: str = "auto") -> str:
    """`requested` accepts both the legacy 5.0 names and 6.0 style ids."""
    legacy = {
        "stud": "stud", "stylized_low_poly": "stylized_low_poly", "fantasy_cinematic": "fantasy_cinematic",
        "cosmic_art": "cosmic_art", "sci_fi_clean": "sci_fi_clean", "natural_realism": "natural_realism",
    }
    if requested in legacy:
        return legacy[requested]
    text = (idea or "").lower()
    for key, words in STYLE_KEYWORDS.items():
        if any(w in text for w in words):
            return key
    return "stylized_low_poly"


def choose_theme(idea: str, requested: str = "auto") -> str:
    theme_keywords = {
        "cosmic": ["cosmic", "space", "galaxy", "nebula", "star", "celestial", "חלל", "קוסמי", "גלקסיה"],
        "sci_fi": ["sci-fi", "scifi", "futuristic", "cyber", "robot", "עתידני"],
        "fantasy": ["magic", "fantasy", "enchanted", "rune", "wizard", "פנטזיה", "קסום"],
        "crystal": ["crystal", "gem", "geode", "קריסטל", "גביש"],
        "steampunk": ["steampunk", "brass", "clockwork", "קיטור"],
    }
    if requested in THEME_ACCENTS:
        return requested
    text = (idea or "").lower()
    for key, words in theme_keywords.items():
        if any(w in text for w in words):
            return key
    return "natural"


def hex_to_rgb(value: str) -> list[int]:
    value = value.lstrip("#")
    return [int(value[i:i + 2], 16) for i in (0, 2, 4)]


def build_art_direction(idea: str, style_key: str, theme: str, genre_profile: str = "") -> dict:
    style = STYLE_LIBRARY[style_key]
    accent_theme = THEME_ACCENTS.get(theme, THEME_ACCENTS["natural"])
    palette = list(style["palette"])
    roles = dict(zip(PALETTE_ROLES, palette))
    # The theme owns the accent so cosmic/sci-fi/fantasy ideas do not inherit a forest accent.
    roles["accent"] = accent_theme["accent"]
    reference = match_reference(idea, genre_profile)
    return {
        "style": style_key,
        "style_label": style["label"],
        "theme": theme,
        "mood": MOOD_BY_STYLE.get(style_key, style["label"]),
        "geometry_language": style["geometry"],
        "detail_bias": style["detail_bias"],
        "avoid": list(style["avoid"]),
        "palette": roles,
        "materials": dict(style["materials"]),
        "lighting": dict(style["lighting"]),
        "target_part_ratio": style["target_part_ratio"],
        "props": list(accent_theme["props"]),
        "vfx": list(accent_theme["vfx"]),
        "references": [{"id": reference["id"], "label": reference["label"],
                        "density": reference["density"], "scale": reference["scale"],
                        "composition": reference["composition"]}],
        "design_principles": principles_for([reference]),
        "critique_targets": {
            "min_visual_score": 85,
            "max_repeated_silhouette_share": 0.45,
            "min_asset_variety_per_region": 4,
            "max_flat_palette_delta": 0.35,
        },
    }


def palette_hex_list(art: dict) -> list[str]:
    return [art["palette"][role] for role in PALETTE_ROLES]


def style_summary(art: dict) -> str:
    return (f"{art['style_label']} / {art['theme']}: {art['mood']}. "
            f"Geometry: {art['geometry_language']}. Palette {', '.join(palette_hex_list(art))}.")
