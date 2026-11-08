#!/usr/bin/env python3
"""Corrected warehouse diagnostic.

Parses the canonical RBXMX with the REAL property format (typed elements
inside a <Properties> container), walks the nested <Item> hierarchy,
composes each MeshPart world CFrame from ancestor Model pivots, and diffs
against the flat model.json. Read-only: prints only, never writes.
"""
import xml.etree.ElementTree as ET
import json
import sys

RBXMX = "src/ServerStorage/GeneratedAssets/abandoned_warehouse_interior_01.rbxmx"
MODEL_JSON = "src/Workspace/abandoned_warehouse_interior_01.model.json"
TOL = 1e-3

CF_KEYS = ("X", "Y", "Z", "R00", "R01", "R02", "R10", "R11", "R12", "R20", "R21", "R22")

# ---------- CFrame math ----------
def cf_from12(v):
    p = [v[0], v[1], v[2]]
    R = [[v[3], v[4], v[5]], [v[6], v[7], v[8]], [v[9], v[10], v[11]]]
    return (R, p)

def cf_mul(A, B):
    R1, p1 = A
    R2, p2 = B
    R = [[sum(R1[i][k] * R2[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    p = [p1[i] + R1[i][0] * p2[0] + R1[i][1] * p2[1] + R1[i][2] * p2[2] for i in range(3)]
    return (R, p)

def cf_list(c):
    R, p = c
    return [R[0][0], R[0][1], R[0][2], R[1][0], R[1][1], R[1][2],
            R[2][0], R[2][1], R[2][2], p[0], p[1], p[2]]

def cf_close(a, b, tol=TOL):
    if a is None or b is None:
        return a is None and b is None
    la, lb = cf_list(a), cf_list(b)
    return all(abs(x - y) <= tol for x, y in zip(la, lb))

IDENTITY = cf_from12([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1])

# ---------- Parse RBXMX (real format) ----------
def parse_properties(item):
    d = {}
    props_el = item.find("Properties")
    if props_el is None:
        return d
    for p in props_el:
        name = p.get("name")
        if name is None:
            continue
        tag = p.tag.split("}")[-1]
        if tag == "Vector3":
            d[name] = [float(p.findtext(c)) for c in ("X", "Y", "Z")]
        elif tag == "CoordinateFrame":
            d[name] = [float(p.findtext(c)) for c in CF_KEYS]
        elif tag == "OptionalCoordinateFrame":
            cf = p.find("CFrame")
            if cf is not None:
                d[name] = [float(cf.findtext(c)) for c in CF_KEYS]
        else:
            d[name] = p.text
    return d

tree = ET.parse(RBXMX)
root = tree.getroot()

parts = []
model_count = [0]

def walk(item, chain):
    cls = item.get("class")
    props = parse_properties(item)
    if cls == "Model":
        model_count[0] += 1
        chain = chain + [(props.get("Name"), props)]
    if cls == "MeshPart":
        parts.append({"name": props.get("Name"), "props": props, "chain": chain})
    for ch in item.findall("Item"):
        walk(ch, chain)

ri = root.find("Item")
if ri is None:
    ri = root
walk(ri, [])

print("MODELS:", model_count[0], " MESHPARTS:", len(parts))

# ---------- Compose world CFrame per part ----------
for part in parts:
    local = cf_from12(part["props"]["CFrame"]) if "CFrame" in part["props"] else None
    # candidate 1: product of ALL ancestor Model WorldPivotData (relative interpretation)
    composed_all = IDENTITY
    for (_nm, mprops) in part["chain"]:
        wpd = mprops.get("WorldPivotData")
        if wpd:
            composed_all = cf_mul(composed_all, cf_from12(wpd))
    if local:
        composed_all = cf_mul(composed_all, local)
    # candidate 2: immediate parent Model WorldPivotData only (absolute interpretation)
    parent_wpd = None
    if part["chain"]:
        parent_wpd = part["chain"][-1][1].get("WorldPivotData")
    composed_parent = cf_mul(cf_from12(parent_wpd), local) if (parent_wpd and local) else local
    part["raw"] = local
    part["composed_all"] = composed_all
    part["composed_parent"] = composed_parent

# ---------- Load model.json ----------
with open(MODEL_JSON) as f:
    mj = json.load(f)

def mj_parts_list(obj):
    if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
        if any(("Name" in x) for x in obj):
            return obj
    if isinstance(obj, list):
        for x in obj:
            r = mj_parts_list(x)
            if r:
                return r
    elif isinstance(obj, dict):
        for v in obj.values():
            r = mj_parts_list(v)
            if r:
                return r
    return None

mj_parts = mj_parts_list(mj) or []
print("MJ PARTS:", len(mj_parts))

def mj_prop(part, key):
    if "Properties" in part and isinstance(part["Properties"], dict):
        return part["Properties"].get(key)
    return part.get(key)

def mj_cf(part):
    v = mj_prop(part, "CFrame")
    if isinstance(v, (list, tuple)) and len(v) == 12:
        return cf_from12([float(x) for x in v])
    return None

def mj_size(part):
    v = mj_prop(part, "Size")
    if isinstance(v, (list, tuple)) and len(v) == 3:
        return [float(x) for x in v]
    return None

def size_close(a, b, tol=TOL):
    if a is None or b is None:
        return a is None and b is None
    return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))

# ---------- Compare ----------
rbx_by_name = {}
for p in parts:
    rbx_by_name.setdefault(p["name"], []).append(p)

cnt = {"raw": 0, "composed_all": 0, "composed_parent": 0, "size": 0,
       "meshid": 0, "mat": 0, "color": 0}
matched = 0
unmatched = []
detail_rows = []

for mp in mj_parts:
    nm = mp.get("Name")
    if nm not in rbx_by_name:
        unmatched.append(nm)
        continue
    rp = rbx_by_name[nm][0]
    matched += 1
    mcf = mj_cf(mp)
    msize = mj_size(mp)
    mid = mj_prop(mp, "MeshId")
    mat = mj_prop(mp, "Material")
    col = mj_prop(mp, "Color")
    rprops = rp["props"]
    r_mid = rprops.get("MeshId")
    r_mat = rprops.get("Material")
    r_col = rprops.get("Color")
    r_size = rprops.get("Size")

    if cf_close(mcf, rp["raw"]):
        cnt["raw"] += 1
    if cf_close(mcf, rp["composed_all"]):
        cnt["composed_all"] += 1
    if cf_close(mcf, rp["composed_parent"]):
        cnt["composed_parent"] += 1
    if size_close(msize, r_size):
        cnt["size"] += 1
    if str(mid) == str(r_mid):
        cnt["meshid"] += 1
    if str(mat) == str(r_mat):
        cnt["mat"] += 1
    if col is not None and r_col is not None and all(
        abs(float(a) - float(b)) <= TOL for a, b in zip(col, r_col)
    ):
        cnt["color"] += 1

    if len(detail_rows) < 5:
        detail_rows.append((nm, mcf, rp["raw"], rp["composed_all"], rp["composed_parent"],
                            [a for a in rp["chain"]]))

print("\nMATCHED:", matched, " UNMATCHED:", len(unmatched))
if unmatched:
    print("UNMATCHED NAMES:", unmatched[:10])
print("MJ CFrame == RBX raw stored:", cnt["raw"], "/", matched)
print("MJ CFrame == RBX composed_all (all ancestor pivots):", cnt["composed_all"], "/", matched)
print("MJ CFrame == RBX composed_parent (immediate parent pivot):", cnt["composed_parent"], "/", matched)
print("MJ Size == RBX Size:", cnt["size"], "/", matched)
print("MJ MeshId == RBX MeshId:", cnt["meshid"], "/", matched)
print("MJ Material == RBX Material:", cnt["mat"], "/", matched)
print("MJ Color == RBX Color:", cnt["color"], "/", matched)

print("\n--- DETAIL (first 5 matched parts) ---")
for nm, mcf, raw, comp_all, comp_parent, chain in detail_rows:
    print(f"\nPART {nm}")
    print(f"  MJ_CFrame      : {cf_list(mcf) if mcf else None}")
    print(f"  RBX_raw        : {cf_list(raw) if raw else None}")
    print(f"  RBX_comp_all   : {cf_list(comp_all) if comp_all else None}")
    print(f"  RBX_comp_parent: {cf_list(comp_parent) if comp_parent else None}")
    print(f"  ancestor chain (root->parent):")
    for (anm, mprops) in chain:
        wpd = mprops.get("WorldPivotData")
        print(f"    Model {anm!r} WorldPivotData={cf_list(cf_from12(wpd)) if wpd else None}")

print("\nDONE.")