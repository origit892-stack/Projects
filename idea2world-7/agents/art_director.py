"""Art Director: defines the visual language every later stage is judged against."""
from __future__ import annotations

from research.reference_library import STYLE_LIBRARY
from research.style_analyzer import (PALETTE_ROLES, build_art_direction, choose_style,
                                     choose_theme, palette_hex_list)

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="art_director",
    title="Art Director",
    role="Visual language: palette, materials, lighting, silhouette rules and density.",
    system_prompt=(
        "You are an art director for stylized Roblox worlds. You define transferable visual languages, "
        "never copies of another game's art. Answer in strict JSON only. Palettes must be coherent: one "
        "dominant field colour, two structural mid-tones, one accent reserved for interactables and a "
        "highlight for text/UI. Every rule you give must be checkable in a screenshot."
    ),
    skills=["colour theory", "material language", "lighting", "silhouette design", "visual hierarchy"],
    artifacts=["art_direction"],
    authority="owner:visual",
)


class ArtDirector(BaseAgent):
    def direct(self, idea: str, settings: dict, genre: str, brain_meta: dict | None = None) -> dict:
        style_key = choose_style(idea, settings.get("visual_style") or settings.get("style", "auto"))
        theme = choose_theme(idea, settings.get("visual_theme", "auto"))
        art = build_art_direction(idea, style_key, theme, genre)
        art["vfx_density"] = max(0.0, min(1.0, float(settings.get("vfx_density", 65)) / 100.0))
        art["detail_density"] = max(0.0, min(1.0, float(settings.get("detail", 70) if isinstance(settings.get("detail"), (int, float))
                                                          else 70) / 100.0))
        art["lighting_profile"] = STYLE_LIBRARY[style_key]["lighting"]
        art["palette_roles"] = PALETTE_ROLES

        prompt = (
            "Refine the art direction for this world so it feels specific to the idea. Return JSON with "
            "keys: mood (one sentence), palette (object with exactly field, field_alt, structure, "
            "structure_alt, accent, highlight as #rrggbb), material_notes (one sentence), "
            "lighting_note (one sentence), signature_detail (one concrete repeated visual motif), "
            "avoid (array of 2-4 things to avoid). Current direction:\n"
            f"{art['style_label']} / {art['theme']}, geometry: {art['geometry_language']}, "
            f"palette: {art['palette']}. Idea: {idea}"
        )
        refined, meta = self.refine(prompt, {})
        if refined:
            palette = refined.get("palette")
            if isinstance(palette, dict):
                merged = dict(art["palette"])
                for role in PALETTE_ROLES:
                    value = palette.get(role)
                    if isinstance(value, str) and _valid_hex(value):
                        merged[role] = value.lower()
                if len({merged[r] for r in PALETTE_ROLES}) >= 4:
                    art["palette"] = merged
            for key, field in (("mood", "mood"), ("material_notes", "material_notes"),
                               ("lighting_note", "lighting_note"), ("signature_detail", "signature_detail")):
                if isinstance(refined.get(key), str) and refined[key].strip():
                    art[field] = refined[key].strip()
            avoid = refined.get("avoid")
            if isinstance(avoid, list) and all(isinstance(a, str) for a in avoid[:4]):
                art["avoid"] = avoid[:4]
        art["brain"] = meta
        art["palette_list"] = palette_hex_list(art)
        self.emit("direct", f"style={style_key} theme={theme} mood={art['mood'][:60]}")
        return art

    def evaluate_palette(self, art: dict) -> dict:
        """Cheap, objective checks the visual critic reuses later."""
        colors = [art["palette"][r] for r in PALETTE_ROLES]
        luminances = [_luminance(c) for c in colors]
        contrast = max(luminances) - min(luminances)
        return {"distinct_colors": len(set(colors)), "contrast": round(contrast, 3),
                "accent_is_isolated": colors[4] == art["palette"]["accent"],
                "passed": len(set(colors)) >= 5 and contrast > 0.18}


def _valid_hex(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 7 or not value.startswith("#"):
        return False
    try:
        int(value[1:], 16)
        return True
    except ValueError:
        return False


def _luminance(hex_color: str) -> float:
    value = hex_color.lstrip("#")
    r, g, b = (int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def direct(idea: str, settings: dict, genre: str, brain=None, events=None) -> dict:
    return ArtDirector(SPEC, brain, events).direct(idea, settings, genre)
