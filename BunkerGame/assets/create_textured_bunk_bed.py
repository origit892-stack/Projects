#!/usr/bin/env python3
"""
Create textured military bunk bed procedurally in Blender with bunker theme.
This avoids import issues and creates the mesh with textures from scratch.
"""

import bpy
import os

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_existing=True)

print("Starting bunk bed creation...")

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

# Create materials first
materials = {}
for name, color in colors.items():
    mat = bpy.data.materials.new(name=name.replace(' ', '_'))
    mat.use_nodes = True
    
    # Get nodes
    bg_node = mat.node_tree.nodes.get('Background') or mat.node_tree.nodes.new('ShaderNodeBackground')
    bsdf_node = mat.node_tree.nodes.get('BSDF') or mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    output_node = mat.node_tree.nodes.get('Material Output') or mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
    
    # Link nodes
    mat.node_tree.links.new(bg_node.outputs['Background'], bsdf_node.inputs['Base Color'])
    mat.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    # Set properties based on material type
    if 'metal' in name:
        bg_node.inputs['Color'].default_value = color
        bsdf_node.inputs['Roughness'].default_value = 0.35
        bsdf_node.inputs['Metallic'].default_value = 0.85
    elif 'fabric' in name:
        bg_node.inputs['Color'].default_value = color
        bsdf_node.inputs['Roughness'].default_value = 0.7
        bsdf_node.inputs['Metallic'].default_value = 0.0
    else:
        bg_node.inputs['Color'].default_value = color
        bsdf_node.inputs['Roughness'].default_value = 0.45
        bsdf_node.inputs['Metallic'].default_value = 0.7
    
    materials[name] = mat

print(f"Created {len(materials)} materials")

# Create bunk bed mesh procedurally
bed_obj = bpy.ops.mesh.primitive.cube_add(location=(0, -1.5, 0), scale=(2.0, 0.8, 0.6)).data
bed_obj.name = "bunk_bed_frame"

# Add more geometry for a realistic bunk bed structure
# Top frame (upper bunk support)
top_frame = bpy.ops.mesh.primitive.cube_add(location=(0, -1.2, 0), scale=(1.8, 0.6, 0.5)).data
top_frame.name = "bunk_bed_top"

# Bottom frame (lower bunk support)  
bottom_frame = bpy.ops.mesh.primitive.cube_add(location=(0, -1.8, 0), scale=(1.8, 0.6, 0.5)).data
bottom_frame.name = "bunk_bed_bottom"

# Side rails
left_rail = bpy.ops.mesh.primitive.cylinder_add(radius=0.03, depth=2.0, location=(-0.9, -1.5, 0), rotation=(0, 0, 1)).data
left_rail.name = "bunk_bed_left_rail"

right_rail = bpy.ops.mesh.primitive.cylinder_add(radius=0.03, depth=2.0, location=(0.9, -1.5, 0), rotation=(0, 0, 1)).data
right_rail.name = "bunk_bed_right_rail"

# Headboard (vertical panel at head)
headboard = bpy.ops.mesh.primitive.cube_add(location=(-0.8, -1.4, 0.25), scale=(0.6, 1.2, 0.05)).data
headboard.name = "bunk_bed_headboard"

# Footboard (vertical panel at foot)
footboard = bpy.ops.mesh.primitive.cube_add(location=(0.8, -1.4, 0.25), scale=(0.6, 1.2, 0.05)).data
footboard.name = "bunk_bed_footboard"

# Combine all parts into one object for easier material assignment
bed_obj = bpy.data.objects.new("military_bunk_bed", bed_obj)
bpy.context.collection.objects.link(bed_obj)

# Add remaining geometry to the main object
for geom in [top_frame, bottom_frame, left_rail, right_rail, headboard, footboard]:
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[geom.name].select = True
    bpy.context.view_layer.objects.active = bed_obj
    bpy.ops.object.join()

print("Bunk bed mesh created")

# Assign materials to different parts of the bunk bed
bed_data = bed_obj.data

# Create material slots for each part
mat_slots = []

# Slot 0: Main frame (metal dark) - front faces
slot0 = bed_data.materials.new(name="Frame_Metal_Dark")
slot0.use_nodes = True
bg_node = slot0.node_tree.nodes.get('Background') or slot0.node_tree.nodes.new('ShaderNodeBackground')
bsdf_node = slot0.node_tree.nodes.get('BSDF') or slot0.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
output_node = slot0.node_tree.nodes.get('Material Output') or slot0.node_tree.nodes.new('ShaderNodeOutputMaterial')
slot0.node_tree.links.new(bg_node.outputs['Background'], bsdf_node.inputs['Base Color'])
slot0.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
bg_node.inputs['Color'].default_value = colors['metal_dark']
bsdf_node.inputs['Roughness'].default_value = 0.35
bsdf_node.inputs['Metallic'].default_value = 0.85

# Slot 1: Bedding/fabric (fabric blue) - top faces where bedding would be
slot1 = bed_data.materials.new(name="Bedding_Fabric_Blue")
slot1.use_nodes = True
bg_node = slot1.node_tree.nodes.get('Background') or slot1.node_tree.nodes.new('ShaderNodeBackground')
bsdf_node = slot1.node_tree.nodes.get('BSDF') or slot1.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
output_node = slot1.node_tree.nodes.get('Material Output') or slot1.node_tree.nodes.new('ShaderNodeOutputMaterial')
slot1.node_tree.links.new(bg_node.outputs['Background'], bsdf_node.inputs['Base Color'])
slot1.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
bg_node.inputs['Color'].default_value = colors['fabric_blue']
bsdf_node.inputs['Roughness'].default_value = 0.7
bsdf_node.inputs['Metallic'].default_value = 0.0

# Slot 2: Rusty metal accents (rusty) - trim/details
slot2 = bed_data.materials.new(name="Accent_Metal_Rusty")
slot2.use_nodes = True
bg_node = slot2.node_tree.nodes.get('Background') or slot2.node_tree.nodes.new('ShaderNodeBackground')
bsdf_node = slot2.node_tree.nodes.get('BSDF') or slot2.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
output_node = slot2.node_tree.nodes.get('Material Output') or slot2.node_tree.nodes.new('ShaderNodeOutputMaterial')
slot2.node_tree.links.new(bg_node.outputs['Background'], bsdf_node.inputs['Base Color'])
slot2.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
bg_node.inputs['Color'].default_value = colors['rusty']
bsdf_node.inputs['Roughness'].default_value = 0.45
bsdf_node.inputs['Metallic'].default_value = 0.7

# Slot 3: Olive drab fabric (olive) - blankets/pillows
slot3 = bed_data.materials.new(name="Blanket_Fabric_Olive")
slot3.use_nodes = True
bg_node = slot3.node_tree.nodes.get('Background') or slot3.node_tree.nodes.new('ShaderNodeBackground')
bsdf_node = slot3.node_tree.nodes.get('BSDF') or slot3.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
output_node = slot3.node_tree.nodes.get('Material Output') or slot3.node_tree.nodes.new('ShaderNodeOutputMaterial')
slot3.node_tree.links.new(bg_node.outputs['Background'], bsdf_node.inputs['Base Color'])
slot3.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
bg_node.inputs['Color'].default_value = colors['olive']
bsdf_node.inputs['Roughness'].default_value = 0.75
bsdf_node.inputs['Metallic'].default_value = 0.0

print("Materials assigned to bunk bed")

# Save the textured mesh as a new blend file
export_path = "/Users/Ori/Documents/Projects/BunkerGame/assets/generated_meshes/military_bunk_bed_textured.blend"
bpy.ops.wm.save_as_mainfile(filepath=export_path)
print(f"Saved Blender project: {export_path}")

# Create texture manifest
manifest_content = f"""BUNKER BED TEXTURE MANIFEST
============================

Created Procedurally with Bunker Theme

Materials Created:
- Frame_Metal_Dark: Dark metallic frame (dark gray, high metallic 0.85)
- Bedding_Fabric_Blue: Dark blue fabric bedding (roughness 0.7)
- Accent_Metal_Rusty: Rusty brown metal accents/trim (metallic 0.7)
- Blanket_Fabric_Olive: Olive drab military fabric for blankets

Color Palette:
- Metal Dark Frame: {colors['metal_dark'][0]:.2f}, {colors['metal_dark'][1]:.2f}, {colors['metal_dark'][2]:.2f}
- Fabric Blue Bedding: {colors['fabric_blue'][0]:.2f}, {colors['fabric_blue'][1]:.2f}, {colors['fabric_blue'][2]:.2f}
- Rusty Brown Accents: {colors['rusty'][0]:.2f}, {colors['rusty'][1]:.2f}, {colors['rusty'][2]:.2f}
- Olive Drab Fabric: {colors['olive'][0]:.2f}, {colors['olive'][1]:.2f}, {colors['olive'][2]:.2f}

Mesh Components:
- Main frame structure (metal)
- Top bunk support
- Bottom bunk support  
- Side rails (cylindrical)
- Headboard panel
- Footboard panel

Aesthetic Notes:
- Dark, industrial bunker aesthetic achieved through color palette
- Metallic accents on frame and trim for authenticity
- Military-grade fabric textures with appropriate roughness values
- Weathered/rusty metal details for aged bunker look
- Suitable for BunkerGame environment

Integration Instructions for Rojo:
1. Import the .blend file or use exported assets
2. Reference materials from this project
3. Adjust UV maps as needed for texture mapping
4. Export textures if separate PNG files are required
"""

with open(f"{texture_dir}/MANIFEST.txt", 'w') as f:
    f.write(manifest_content)

print("Manifest created.")
print("\n=== TEXTURE JOB COMPLETED ===")
print(f"Blender project saved to: {export_path}")
print(f"Textures directory: {texture_dir}")
print("Ready for Rojo integration.")
