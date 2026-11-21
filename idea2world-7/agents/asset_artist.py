"""Asset Artist: decides what must be modelled, how it is obtained and how it is validated."""
from __future__ import annotations

from assets.asset_registry import build_manifest, reuse_stats
from assets.asset_validator import validate_asset_manifest
from assets.import_pipeline import mesh_request_plan
from assets.material_generator import apply_material_variants, build_material_plan

from .base import AgentSpec, BaseAgent

SPEC = AgentSpec(
    id="asset_artist",
    title="3D Asset Artist",
    role="Models, textures, materials and the assets the world actually needs.",
    system_prompt=(
        "You are a stylized 3D asset artist for Roblox. You describe models as readable silhouettes with "
        "a clear primary form, secondary forms and a material story. You never copy a specific game's "
        "asset. Answer in strict JSON only. Every asset must be buildable as a game-ready mesh or as a "
        "layered set of shaped primitives; a stack of boxes is not an asset."
    ),
    skills=["silhouette design", "low-poly modelling", "PBR materials", "modular kits", "LOD"],
    artifacts=["asset_manifest", "material_plan"],
    authority="owner:assets",
)


class AssetArtist(BaseAgent):
    def plan(self, spec) -> dict:
        manifest = build_manifest(spec)
        material_plan = build_material_plan(spec)
        apply_material_variants(spec, material_plan)
        validation = validate_asset_manifest(spec)
        mesh_plan = mesh_request_plan(spec)
        reuse = reuse_stats(spec)
        structures = [a for a in manifest["assets"] if a["category"] == "structure"]
        summary = {
            "assets": len(manifest["assets"]),
            "structures": len(structures),
            "scatter_assets": len(manifest["assets"]) - len(structures),
            "mesh_requests": mesh_plan["count"],
            "materials": len(material_plan["materials"]),
            "material_variants": len(spec.data.get("material_variants") or []),
            "validation": validation,
            "reuse": reuse,
            "mesh_plan": mesh_plan,
            "material_plan": material_plan,
        }
        self.emit("plan", f"{summary['assets']} assets ({summary['structures']} structures), "
                          f"{summary['mesh_requests']} mesh requests, {summary['materials']} materials")
        return summary


def plan(spec, brain=None, events=None) -> dict:
    return AssetArtist(SPEC, brain, events).plan(spec)
