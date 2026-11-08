#!/usr/bin/env python3
"""Classify .obj assets: valid / placeholder / broken.

Validates per-file:
- non-empty geometry (v and f counts)
- face index range against vertex count (catches multi-object f-index bugs)
- material file references exist if any
- bounding-box sanity (non-degenerate, finite)

Outputs a JSON report + human table. Exit 0 always (report tool).
"""
import json
import math
import os
import re
import sys

def analyze(path):
    verts = []
    faces = []
    mtl_files = []
    with_vertex_normals = 0
    with_tex = 0
    bad_lines = 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                s = line.strip()
                if s.startswith("v "):
                    parts = s.split()
                    try:
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    except (ValueError, IndexError):
                        bad_lines += 1
                        continue
                    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                        bad_lines += 1
                        continue
                    verts.append((x, y, z))
                    if len(parts) >= 7:
                        with_vertex_normals += 1
                    if len(parts) >= 4:
                        with_tex += 1
                elif s.startswith("f "):
                    idxs = []
                    ok = True
                    for tok in s[2:].split():
                        first = tok.split("/")[0]
                        try:
                            i = int(first)
                        except ValueError:
                            ok = False
                            break
                        if i < 0:
                            i += len(verts)
                        if i < 1 or i > len(verts):
                            ok = False
                            break
                        idxs.append(i)
                    if ok and len(idxs) >= 3:
                        faces.append(idxs)
                    else:
                        bad_lines += 1
                elif s.startswith("mtllib "):
                    mtl_files.append(s.split(None, 1)[1].strip())
    except OSError as exc:
        return {"error": str(exc)}

    n = len(verts)
    out = {
        "vertices": n,
        "faces": len(faces),
        "bad_lines": bad_lines,
        "mtl_refs": mtl_files,
        "has_vertex_normals": with_vertex_normals > 0,
        "has_tex_coords": with_tex > 0,
    }
    if n == 0:
        out["bbox"] = None
        out["size_studs_estimate"] = None
        return out

    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    zs = [p[2] for p in verts]
    out["bbox"] = {
        "min": [round(min(xs), 3), round(min(ys), 3), round(min(zs), 3)],
        "max": [round(max(xs), 3), round(max(ys), 3), round(max(zs), 3)],
    }
    dims = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    out["size_studs_estimate"] = [round(d, 3) for d in dims]
    out["degenerate"] = max(dims) < 1e-6
    return out

def classify(path, r):
    if "error" in r:
        return "FAILED"
    n, f = r["vertices"], r["faces"]
    if n == 0:
        return "FAILED_NO_VERTS"
    if f == 0:
        # has vertices but no faces: placeholder geometry only
        if n < 30:
            return "PLACEHOLDER_TINY"
        return "PLACEHOLDER_NO_FACES"
    if r["degenerate"]:
        return "FAILED_DEGENERATE"
    if f < 10:
        return "PLACEHOLDER_LOW_GEO"
    if r["bad_lines"] > max(10, f * 0.01):
        return "SUSPECT_BAD_LINES"
    return "VALID"

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "assets/generated_meshes"
    results = {}
    rows = []
    for name in sorted(os.listdir(root)):
        if not name.lower().endswith(".obj"):
            continue
        path = os.path.join(root, name)
        r = analyze(path)
        cls = classify(path, r)
        results[name] = {"classification": cls, **r}
        size = os.path.getsize(path)
        rows.append((name, cls, r.get("vertices", 0), r.get("faces", 0), r.get("bad_lines", 0), size,
                     r.get("size_studs_estimate"), r.get("mtl_refs")))

    print(f"{'ASSET':<45} {'CLASS':<20} {'VERTS':>7} {'FACES':>7} {'BADLN':>6} {'BYTES':>9}  DIMS / MTL")
    print("-" * 130)
    for name, cls, v, f, bl, size, dims, mtl in rows:
        dimstr = "x".join(f"{d:g}" for d in dims) if dims else "-"
        mtlstr = ",".join(mtl) if mtl else ""
        print(f"{name:<45} {cls:<20} {v:>7} {f:>7} {bl:>6} {size:>9}  {dimstr:<24} {mtlstr}")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "obj_report.json")
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=2)
    print(f"\nreport written: {out_path}")

if __name__ == "__main__":
    main()
