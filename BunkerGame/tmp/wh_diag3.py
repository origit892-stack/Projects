#!/usr/bin/env python3
"""Comprehensive warehouse diagnostic. Single script, single run."""
import xml.etree.ElementTree as ET
import json
import re
import sys

RBXMX = "src/ServerStorage/GeneratedAssets/abandoned_warehouse_interior_01.rbxmx"
MODEL_JSON = "src/Workspace/abandoned_warehouse_interior_01.model.json"

# --- 1. Count instances ---
with open(RBXMX) as f:
    raw = f.read()

sa_count = len(re.findall(r'class="SurfaceAppearance"', raw))
tex_count = len(re.findall(r'class="Texture"', raw))
decal_count = len(re.findall(r'class="Decal"', raw))
print(f"SurfaceAppearance: {sa_count}")
print(f"Texture: {tex_count}")
print(f"Decal: {decal_count}")

# --- 2. Parse RBXMX ---
CF_KEYS = ("X", "Y", "Z", "R00", "R01", "R02", "R10", "R11", "R12", "R20", "R21", "R22")

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

# Find all MeshParts and their properties
all_parts = []
def walk(item):
    cls = item.get("class")
    props = parse_properties(item)
    if cls == "MeshPart":
        all_parts.append({"name": props.get("Name"), "props": props})
    for ch in item.findall("Item"):
        walk(ch)

ri = root.find("Item")
if ri is None:
    ri = root
walk(ri)

print(f"\nTotal MeshParts in RBXMX: {len(all_parts)}")

# --- 3. Extract sample part from RBXMX ---
sample_name = "TexturesCom_WindowsBacklit0019_13_M_0"
sample_rbx = None
for p in all_parts:
    if p["name"] == sample_name:
        sample_rbx = p
        break

print(f"\n=== RBXMX sample part: {sample_name} ===")
if sample_rbx:
    for k, v in sorted(sample_rbx["props"].items()):
        print(f"  {k} = {v}")
else:
    print("  NOT FOUND")

# --- 4. Load model.json ---
with open(MODEL_JSON) as f:
    mj = json.load(f)

print(f"\n=== model.json top-level structure ===")
print(f"  ClassName: {mj.get('ClassName')}")
print(f"  Name: {mj.get('Name')}")
print(f"  Has Properties key: {'Properties' in mj}")
if "Properties" in mj:
    print(f"  Properties: {mj['Properties']}")
print(f"  Children count: {len(mj.get('Children', []))}")

# Find sample part in model.json
sample_mj = None
for c in mj.get("Children", []):
    if c.get("Name") == sample_name:
        sample_mj = c
        break

print(f"\n=== model.json sample part: {sample_name} ===")
if sample_mj:
    for k, v in sorted(sample_mj.items()):
        if k == "Name":
            continue
        print(f"  {k} = {json.dumps(v) if isinstance(v, (list, dict)) else v}")
else:
    print("  NOT FOUND")

# --- 5. Compare ---
print(f"\n=== COMPARISON: {sample_name} ===")
if sample_rbx and sample_mj:
    rbx_props = sample_rbx["props"]
    mj_props = sample_mj.get("Properties", sample_mj)
    
    # Properties in RBXMX but not in model.json
    rbx_keys = set(rbx_props.keys())
    mj_keys = set(mj_props.keys())
    
    only_rbx = rbx_keys - mj_keys
    only_mj = mj_keys - rbx_keys
    common = rbx_keys & mj_keys
    
    print(f"  Props in RBXMX only ({len(only_rbx)}): {sorted(only_rbx)}")
    print(f"  Props in model.json only ({len(only_mj)}): {sorted(only_mj)}")
    print(f"  Common props ({len(common)}): {sorted(common)}")
    
    # Check values for common props
    print(f"\n  Value differences:")
    for k in sorted(common):
        rv = rbx_props[k]
        mv = mj_props[k]
        # Normalize for comparison
        rv_s = str(rv)
        mv_s = str(mv)
        if rv_s != mv_s:
            # Try numeric comparison for lists
            if isinstance(rv, list) and isinstance(mv, list):
                try:
                    if all(abs(float(a) - float(b)) < 0.01 for a, b in zip(rv, mv)):
                        continue
                except (ValueError, TypeError):
                    pass
            print(f"    {k}: RBXMX={rv}  MJ={mv}")

# --- 6. Check all parts for SurfaceAppearance ---
print(f"\n=== SurfaceAppearance check ===")
# Check if any MeshPart in RBXMX has a SurfaceAppearance child
sa_parts = []
def walk_sa(item, part_name):
    cls = item.get("class")
    if cls == "SurfaceAppearance":
        sa_parts.append(part_name)
    for ch in item.findall("Item"):
        if cls == "MeshPart":
            props = parse_properties(item)
            walk_sa(ch, props.get("Name"))
        else:
            walk_sa(ch, part_name)

ri2 = root.find("Item")
if ri2 is None:
    ri2 = root
walk_sa(ri2, None)

print(f"  MeshParts with SurfaceAppearance child: {len(sa_parts)}")
if sa_parts:
    print(f"  First 5: {sa_parts[:5]}")

# Check model.json for SurfaceAppearance
mj_sa = 0
for c in mj.get("Children", []):
    if c.get("ClassName") == "SurfaceAppearance":
        mj_sa += 1
    for cc in c.get("Children", []):
        if cc.get("ClassName") == "SurfaceAppearance":
            mj_sa += 1
print(f"  SurfaceAppearance in model.json: {mj_sa}")

print("\nDONE.")