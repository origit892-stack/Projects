"""SVG map preview generated from the WorldSpec.

Used by the app's World Plan screen and included in every export, so a design can be reviewed before
anything is built in Studio. It draws the terrain field, districts, routes, landmarks and spawn.
"""
from __future__ import annotations

import html
import math

PALETTE = {
    "water": "#2f6f8f", "route": "#e6d5aa", "route_main": "#f0e2bd",
    "spawn": "#4ade80", "poi": "#f5c451", "text": "#e8eef5", "bg": "#0d1117",
}


def plan_svg(spec, width: int = 900, height: int = 900, show_heatmap: bool = True) -> str:
    field = spec.heightfield()
    size = float(spec.world.get("size", 2000))
    scale = width / size

    def px(x: float) -> float:
        return (float(x) + size / 2) * scale

    def py(z: float) -> float:
        return (float(z) + size / 2) * scale

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-label="{html.escape(spec.title)} world plan">',
        f'<rect width="{width}" height="{height}" fill="{PALETTE["bg"]}"/>',
    ]

    if show_heatmap:
        step = max(1, field.res // 110)
        cell = field.cell * scale * step
        for j in range(0, field.res - step, step):
            for i in range(0, field.res - step, step):
                h = field.rows[j][i]
                color = _height_color(field, h)
                parts.append(f'<rect x="{px(field.position_of(i)):.1f}" y="{py(field.position_of(j)):.1f}" '
                             f'width="{cell + 1:.2f}" height="{cell + 1:.2f}" fill="{color}"/>')

    # water bodies
    for region in spec.regions:
        if region.get("kind") in ("lake", "coast", "marsh"):
            cx, cz = region.get("center", (0, 0))
            r = float(region.get("radius", 80)) * 0.55
            parts.append(f'<circle cx="{px(cx):.1f}" cy="{py(cz):.1f}" r="{r * scale:.1f}" '
                         f'fill="{PALETTE["water"]}" opacity="0.55"/>')

    # routes
    for path in spec.paths:
        nodes = path.get("nodes") or []
        if len(nodes) < 2:
            continue
        points = " ".join(f"{px(x):.1f},{py(z):.1f}" for x, z in nodes)
        color = PALETTE["route_main"] if path.get("kind") == "main" else PALETTE["route"]
        width_px = max(2.0, float(path.get("width", 10)) * scale)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{width_px:.1f}" '
                     f'stroke-opacity="0.85" stroke-linejoin="round" stroke-linecap="round"/>')

    # districts
    for region in spec.regions:
        cx, cz = region.get("center", (0, 0))
        r = float(region.get("radius", 100))
        parts.append(f'<circle cx="{px(cx):.1f}" cy="{py(cz):.1f}" r="{r * scale:.1f}" fill="none" '
                     f'stroke="#8fb3c9" stroke-opacity="0.35" stroke-width="1" stroke-dasharray="6 6"/>')
        parts.append(f'<text x="{px(cx):.1f}" y="{py(cz) - r * scale - 6:.1f}" fill="{PALETTE["text"]}" '
                     f'font-family="ui-sans-serif,system-ui" font-size="{max(9, width * 0.013):.1f}" '
                     f'text-anchor="middle" opacity="0.85">{html.escape(region.get("name", ""))}</text>')

    # landmarks
    for poi in spec.pois:
        x, y = px(poi.get("x", 0)), py(poi.get("z", 0))
        r = 9 if poi.get("role") == "focal" else 6
        fill = "#ff9f43" if poi.get("role") == "focal" else PALETTE["poi"]
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="#1a1207" stroke-width="1.5"/>')
        if poi.get("role") == "focal" or len(spec.pois) <= 14:
            parts.append(f'<text x="{x + r + 4:.1f}" y="{y + 3.5:.1f}" fill="{PALETTE["text"]}" '
                         f'font-family="ui-sans-serif,system-ui" font-size="{max(8, width * 0.011):.1f}">'
                         f'{html.escape(poi.get("name", ""))}</text>')

    # spawn
    for spawn in spec.spawns:
        x, y = px(spawn.get("x", 0)), py(spawn.get("z", 0))
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{PALETTE["spawn"]}" stroke="#052e16" stroke-width="2"/>')
        parts.append(f'<text x="{x + 10:.1f}" y="{y + 4:.1f}" fill="{PALETTE["spawn"]}" '
                     f'font-family="ui-sans-serif,system-ui" font-size="{max(9, width * 0.012):.1f}">SPAWN</text>')

    # footer / legend
    legend_y = height - 18
    parts.append(f'<text x="14" y="{legend_y}" fill="{PALETTE["text"]}" opacity="0.7" '
                 f'font-family="ui-sans-serif,system-ui" font-size="{max(9, width * 0.012):.1f}">'
                 f'{html.escape(spec.title)} · {len(spec.regions)} districts · {len(spec.pois)} landmarks · '
                 f'{len(spec.paths)} routes · seed {spec.world.get("seed", 0)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def _height_color(field, h: float) -> str:
    water = field.water
    if h < water:
        t = max(0.0, min(1.0, (water - h) / max(1.0, water + 1 - field.min)))
        r, g, b = (28 + int(20 * (1 - t)), 68 + int(30 * (1 - t)), 96 + int(50 * (1 - t)))
    else:
        t = max(0.0, min(1.0, (h - water) / max(1.0, field.max - water)))
        if t < 0.45:
            k = t / 0.45
            r, g, b = 62 + int(30 * k), 96 + int(28 * k), 64 + int(14 * k)
        elif t < 0.78:
            k = (t - 0.45) / 0.33
            r, g, b = 92 + int(38 * k), 124 + int(16 * k), 78 + int(18 * k)
        else:
            k = (t - 0.78) / 0.22
            r, g, b = 130 + int(90 * k), 140 + int(93 * k), 96 + int(130 * k)
    return f"#{r:02x}{g:02x}{b:02x}"


def plan_stats(spec) -> dict:
    return {
        "districts": [{"id": r["id"], "name": r.get("name"), "kind": r.get("kind"),
                       "center": r.get("center"), "radius": r.get("radius")} for r in spec.regions],
        "landmarks": [{"id": p["id"], "name": p.get("name"), "kind": p.get("kind"),
                       "x": p.get("x"), "z": p.get("z"), "role": p.get("role"),
                       "interaction": p.get("interaction")} for p in spec.pois],
        "routes": [{"id": p["id"], "name": p.get("name"), "kind": p.get("kind"),
                    "width": p.get("width"), "nodes": p.get("nodes")} for p in spec.paths],
        "spawn": spec.spawns[0] if spec.spawns else None,
        "water_level": spec.world.get("water_level"),
        "height_range": [round(spec.heightfield().min, 1), round(spec.heightfield().max, 1)],
    }
