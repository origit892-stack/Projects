#!/usr/bin/env python3
"""
Simplified Blender script to texture military_bunk_bed with bunker theme.
"""

import bpy
import os

# Load OBJ file
obj_path = "/Users/Ori/Documents/Projects/BunkerGame/assets/generated_meshes/military_bunk_bed.obj"
bpy.ops.import_scene.obj(filepath=obj_path)

# Get the mesh
bed_obj = bpy.context.object

# Create texture directory
texture_dir = "/Users/Ori/Documents/Projects/BunkerGame/assets/textures/bunk_bed"
os.makedirs(texture_dir, exist_ok=True)

# Define bunker colors
colors = {
    'metal_dark': (0.15, 0.15, 0.18),
    'fabric_blue': (0.1, 0.15, 0.25),
    'rusty': (0.4, 0.25, 0.15),
    'olive': (0.35, 0.45, 0.25)
}

# Create materials for each face/material slot
for i in range(4):
    mat = bed_obj.data.materials.new(name=f"Bunk_Bed_Mat_{i}")
    mat.use_nodes = True
    
    # Get nodes
    bg_node = mat.node_tree.nodes.get('Background') or mat.node_tree.nodes.new('ShaderNodeBackground')
    bsdf_node = mat.node_tree.nodes.get('BSDF') or mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    output_node = mat.node_tree.nodes.get('Material Output') or mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    
    # Link background to BSDF and output
    mat.node_tree.links.new(bg_node.outputs['Background'], bsdf_node.inputs['Base Color'])
    mat.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    # Set material properties based on slot
    if i == 0:
        bg_color = colors['metal_dark']
        roughness = 0.35
        metallic = 0.85
    elif i == 1:
        bg_color = colors['fabric_blue']
        roughness = 0.7
        metallic = 0.0
    elif i == 2:
        bg_color = colors['rusty']
        roughness = 0.45
        metallic = 0.7
    else:
        bg_color = colors['olive']
        roughness = 0.75
        metallic = 0.0
    
    # Set inputs
    bg_node.inputs['Color'].default_value = bg_color
    bsdf_node.inputs['Roughness'].default_value = roughness
    bsdf_node.inputs['Metallic'].default_value = metallic

# Save the textured mesh as a new blend file
export_path = "/Users/Ori/Documents/Projects/BunkerGame/assets/generated_meshes/military_bunk_bed_textured.blend"
bpy.ops.wm.save_as_mainfile(filepath=export_path)

print(f"Textured mesh saved to: {export_path}")

# Create manifest
manifest = f"""BUNKER BED TEXTURE MANIFEST
============================

Materials Created:
- Bunk_Bed_Mat_0: Dark metallic frame (dark gray, high metallic 0.85)
- Bunk_Bed_Mat_1: Dark blue fabric bedding (roughness 0.7)
- Bunk_Bed_Mat_2: Rusty brown metal accents (metallic 0.7)
- Bunk_Bed_Mat_3: Olive drab military fabric

Color Palette:
- Metal Dark: {colors['metal_dark'][0]:.2f}, {colors['metal_dark'][1]:.2f}, {colors['metal_dark'][2]:.2f}
- Fabric Blue: {colors['fabric_blue'][0]:.2f}, {colors['fabric_blue'][1]:.2f}, {colors['fabric_blue'][2]:.2f}
- Rusty Brown: {colors['rusty'][0]:.2f}, {colors['rusty'][1]:.2f}, {colors['rusty'][2]:.2f}
- Olive Drab: {colors['olive'][0]:.2f}, {colors['olive'][1]:.2f}, {colors['olive'][2]:.2f}

Aesthetic: Dark, industrial bunker theme with metallic accents and detailed textures.
"""

with open(f"{texture_dir}/MANIFEST.txt", 'w') as f:
    f.write(manifest)

print("Manifest created.")
print("Texture job completed!")
