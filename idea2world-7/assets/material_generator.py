"""Material plan: consistent PBR intent and Roblox MaterialVariants for the generated world.

Roblox's `generate_material` tool can synthesise materials, but a generated world also needs a
declarative fallback: which base material, how rough, how metallic, and which palette role tints it.
"""
from __future__ import annotations

MATERIAL_PBR = {
    "Grass": {"roughness": 0.92, "metalness": 0.0, "role": "field", "ai_hint": "stylized grass, soft clumps, no tiling seams"},
    "Ground": {"roughness": 0.95, "metalness": 0.0, "role": "field_alt", "ai_hint": "packed earth with small stones and roots"},
    "Rock": {"roughness": 0.85, "metalness": 0.02, "role": "structure", "ai_hint": "faceted stylized rock, soft chipped edges"},
    "Basalt": {"roughness": 0.8, "metalness": 0.05, "role": "structure", "ai_hint": "dark volcanic basalt with cooled striations"},
    "Slate": {"roughness": 0.7, "metalness": 0.05, "role": "structure_alt", "ai_hint": "stacked slate blocks, thin mortar lines"},
    "Cobblestone": {"roughness": 0.78, "metalness": 0.02, "role": "structure_alt", "ai_hint": "rounded cobbles, worn walking surface"},
    "Brick": {"roughness": 0.85, "metalness": 0.0, "role": "structure_alt", "ai_hint": "old red brick with pale mortar"},
    "Concrete": {"roughness": 0.8, "metalness": 0.02, "role": "structure", "ai_hint": "clean poured concrete, subtle panel lines"},
    "Wood": {"roughness": 0.8, "metalness": 0.0, "role": "structure_alt", "ai_hint": "warm timber grain, hand-hewn facets"},
    "WoodPlanks": {"roughness": 0.75, "metalness": 0.0, "role": "structure_alt", "ai_hint": "weathered planks, visible nail heads"},
    "Metal": {"roughness": 0.4, "metalness": 0.85, "role": "accent", "ai_hint": "brushed metal with edge wear"},
    "CorrodedMetal": {"roughness": 0.7, "metalness": 0.6, "role": "structure_alt", "ai_hint": "rusted steel, flaking paint"},
    "Glass": {"roughness": 0.1, "metalness": 0.1, "role": "highlight", "ai_hint": "clean translucent glass", "transparency": 0.4},
    "Water": {"roughness": 0.15, "metalness": 0.0, "role": "field_alt", "ai_hint": "stylized water surface with soft ripples"},
    "Sand": {"roughness": 0.95, "metalness": 0.0, "role": "highlight", "ai_hint": "fine pale sand with subtle wind ripples"},
    "Snow": {"roughness": 0.9, "metalness": 0.0, "role": "highlight", "ai_hint": "soft packed snow, faint blue shadow"},
    "Mud": {"roughness": 0.98, "metalness": 0.0, "role": "structure", "ai_hint": "wet mud with small pools"},
    "Neon": {"roughness": 0.2, "metalness": 0.0, "role": "accent", "ai_hint": "emissive accent surface", "emissive": True},
    "Marble": {"roughness": 0.35, "metalness": 0.05, "role": "highlight", "ai_hint": "pale veined marble"},
    "Fabric": {"roughness": 0.9, "metalness": 0.0, "role": "accent", "ai_hint": "woven cloth with soft folds"},
    "ForceField": {"roughness": 0.1, "metalness": 0.0, "role": "accent", "ai_hint": "energy field", "emissive": True},
    "Glacier": {"roughness": 0.3, "metalness": 0.0, "role": "highlight", "ai_hint": "layered blue ice"},
    "SmoothPlastic": {"roughness": 0.55, "metalness": 0.0, "role": "field", "ai_hint": "soft matte plastic"},
    "Plastic": {"roughness": 0.6, "metalness": 0.0, "role": "field", "ai_hint": "playful plastic"},
}

DEFAULT = {"roughness": 0.8, "metalness": 0.0, "role": "structure", "ai_hint": "stylized surface"}


def build_material_plan(spec) -> dict:
    """One entry per material actually used by the manifest, with counts and an AI prompt."""
    usage: dict[str, int] = {}
    for asset in spec.asset_manifest.get("assets", []):
        for part in asset.get("recipe") or []:
            usage[part.get("material", "SmoothPlastic")] = usage.get(part.get("material", "SmoothPlastic"), 0) + 1
    palette = spec.art.get("palette", {})
    materials = []
    for name, count in sorted(usage.items(), key=lambda kv: -kv[1]):
        pbr = {**DEFAULT, **MATERIAL_PBR.get(name, {})}
        materials.append({
            "name": name,
            "baseMaterial": name if name in MATERIAL_PBR else "SmoothPlastic",
            "targetColor": palette.get(pbr.get("role", "structure"), "#9aa4ae"),
            "roughness": pbr["roughness"],
            "metalness": pbr["metalness"],
            "emissive": bool(pbr.get("emissive")),
            "transparency": pbr.get("transparency", 0.0),
            "aiPrompt": (f"{pbr['ai_hint']}, seamless stylized game material, {pbr['roughness']:.2f} roughness, "
                         f"matching palette {palette.get(pbr.get('role', 'structure'), '#9aa4ae')}, "
                         "tileable, no text, no logos"),
            "partCount": count,
        })
    ai_materials = [m for m in materials if m["partCount"] >= 4 and m["name"] not in ("Neon", "ForceField", "Glass")]
    return {
        "materials": materials,
        "ai_generate_queue": ai_materials[:10],
        "note": ("Base materials are built into Roblox and always work. MaterialVariants are an upgrade: "
                 "generate them with Studio's material tool or import PBR sets, then assign by name."),
    }


def apply_material_variants(spec, material_plan: dict) -> dict:
    """MaterialVariant specs the Studio bridge can apply after a build."""
    variants = []
    for material in material_plan.get("ai_generate_queue", []):
        variants.append({
            "name": f"I2W_{material['name']}",
            "baseMaterial": material["baseMaterial"],
            "color": material["targetColor"],
            "roughness": material["roughness"],
            "metalness": material["metalness"],
            "source": "generate_material",
            "prompt": material["aiPrompt"],
        })
    spec.data["material_variants"] = variants
    return {"variants": len(variants)}
