#!/usr/bin/env python3
"""
Blender script to texture military_bunk_bed with bunker theme.
Creates dark, metallic, and detailed textures matching industrial bunker aesthetic.
"""

import bpy
import os

# Clear existing scene if needed (optional)
bpy.ops.wm.read_factory_settings(use_existing=True)

# Load the OBJ file
obj_path = "/Users/Ori/Documents/Projects/BunkerGame/assets/generated_meshes/military_bunk_bed.obj"
if os.path.exists(obj_path):
    bpy.ops.import_scene.obj(filepath=obj_path)
    print(f"Loaded: {obj_path}")
else:
    print(f"Warning: OBJ file not found at {obj_path}")

# Get the imported mesh (first object in scene)
objects = bpy.data.objects
if objects:
    bed_obj = objects[0]
    
    # Create texture directory
    texture_dir = "/Users/Ori/Documents/Projects/BunkerGame/assets/textures/bunk_bed"
    os.makedirs(texture_dir, exist_ok=True)
    
    print(f"Created texture directory: {texture_dir}")
    
    # Define bunker theme colors (dark, metallic palette)
    dark_gray = (0.15, 0.15, 0.18)  # Dark gray for metal surfaces
    rusty_brown = (0.4, 0.25, 0.15)  # Rusty brown for aged metal
    olive_drab = (0.35, 0.45, 0.25)  # Military green/olive
    dark_blue = (0.1, 0.15, 0.25)   # Dark blue-gray for fabric
    
    # Create materials for different parts of the bunk bed
    
    # 1. Metal frame material (dark metallic)
    metal_mat = bpy.data.materials.new(name="Bunker_Metal_Dark")
    metal_mat.use_nodes = True
    bsdf = metal_mat.node_tree.nodes["BSDF"]
    
    # Create nodes for dark metallic finish
    metal_mat.node_tree.links.new(bsdf.inputs['Base Color'], 
                                   material_node.outputs['Color'])
    
    # Add background node for base color
    bg_node = metal_mat.node_tree.nodes.new('ShaderNodeBackground')
    bg_color = metal_mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    
    # Set up dark metallic shader network
    bg_node.inputs['Color'].default_value = dark_gray
    bg_node.inputs['Strength'].default_value = 0.5
    
    bsdf.inputs['Base Color'].default_value = dark_gray
    bsdf.inputs['Roughness'].default_value = 0.3  # Slightly rough for industrial look
    bsdf.inputs['Metallic'].default_value = 0.85  # High metallic
    
    metal_mat.node_tree.links.new(bg_node.outputs['Background'], 
                                   material_node.inputs['Background'])
    
    # Create output node if not exists
    mat_output = metal_mat.node_tree.nodes.get('Material Output')
    if not mat_output:
        mat_output = metal_mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        metal_mat.node_tree.links.new(bg_node.outputs['Background'], 
                                       mat_output.inputs['Surface'])
    
    # 2. Fabric material (dark bedding)
    fabric_mat = bpy.data.materials.new(name="Bunker_Fabric_Dark")
    fabric_mat.use_nodes = True
    
    bg_fabric = fabric_mat.node_tree.nodes.new('ShaderNodeBackground')
    bsdf_fabric = fabric_mat.node_tree.nodes.get("BSDF")
    
    if not bsdf_fabric:
        bsdf_fabric = fabric_mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    
    bg_fabric.inputs['Color'].default_value = dark_blue
    bg_fabric.inputs['Strength'].default_value = 0.8
    
    bsdf_fabric.inputs['Base Color'].default_value = dark_blue
    bsdf_fabric.inputs['Roughness'].default_value = 0.7  # Fabric-like roughness
    bsdf_fabric.inputs['Metallic'].default_value = 0.0
    
    fabric_mat.node_tree.links.new(bg_fabric.outputs['Background'], 
                                   mat_output.inputs['Surface']) if mat_output else None
    
    # 3. Rusty metal material (for accents)
    rusty_mat = bpy.data.materials.new(name="Bunker_Metal_Rusty")
    rusty_mat.use_nodes = True
    
    bg_rusty = rusty_mat.node_tree.nodes.new('ShaderNodeBackground')
    bsdf_rusty = rusty_mat.node_tree.nodes.get("BSDF")
    
    if not bsdf_rusty:
        bsdf_rusty = rusty_mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    
    bg_rusty.inputs['Color'].default_value = rusty_brown
    bg_rusty.inputs['Strength'].default_value = 0.6
    
    bsdf_rusty.inputs['Base Color'].default_value = rusty_brown
    bsdf_rusty.inputs['Roughness'].default_value = 0.4
    bsdf_rusty.inputs['Metallic'].default_value = 0.7
    
    # 4. Olive drab fabric (for blankets/pillows)
    olive_mat = bpy.data.materials.new(name="Bunker_Fabric_Olive")
    olive_mat.use_nodes = True
    
    bg_olive = olive_mat.node_tree.nodes.new('ShaderNodeBackground')
    bsdf_olive = olive_mat.node_tree.nodes.get("BSDF")
    
    if not bsdf_olive:
        bsdf_olive = olive_mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    
    bg_olive.inputs['Color'].default_value = olive_drab
    bg_olive.inputs['Strength'].default_value = 0.8
    
    bsdf_olive.inputs['Base Color'].default_value = olive_drab
    bsdf_olive.inputs['Roughness'].default_value = 0.75
    bsdf_olive.inputs['Metallic'].default_value = 0.0
    
    # Assign materials to mesh parts (simplified - assign all for now)
    if bed_obj.data.materials:
        print("Existing materials found, updating...")
    
    # Create new material slots and assign
    mat_slots = []
    for i in range(4):  # Assume up to 4 faces/materials
        slot = bed_obj.data.materials.new(name=f"Bunk_Bed_Mat_{i}")
        if i == 0:
            slot.use_nodes = True
            bg_node = slot.node_tree.nodes.new('ShaderNodeBackground')
            bsdf_node = slot.node_tree.nodes.get("BSDF") or slot.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
            mat_output = slot.node_tree.nodes.get('Material Output') or slot.node_tree.nodes.new('ShaderNodeOutputMaterial')
            
            bg_node.inputs['Color'].default_value = dark_gray
            bsdf_node.inputs['Base Color'].default_value = dark_gray
            bsdf_node.inputs['Roughness'].default_value = 0.35
            bsdf_node.inputs['Metallic'].default_value = 0.8
            
            slot.node_tree.links.new(bg_node.outputs['Background'], mat_output.inputs['Surface'])
        elif i == 1:
            slot.use_nodes = True
            bg_node = slot.node_tree.nodes.new('ShaderNodeBackground')
            bsdf_node = slot.node_tree.nodes.get("BSDF") or slot.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
            mat_output = slot.node_tree.nodes.get('Material Output') or slot.node_tree.nodes.new('ShaderNodeOutputMaterial')
            
            bg_node.inputs['Color'].default_value = dark_blue
            bsdf_node.inputs['Base Color'].default_value = dark_blue
            bsdf_node.inputs['Roughness'].default_value = 0.7
            bsdf_node.inputs['Metallic'].default_value = 0.0
            
            slot.node_tree.links.new(bg_node.outputs['Background'], mat_output.inputs['Surface'])
        elif i == 2:
            slot.use_nodes = True
            bg_node = slot.node_tree.nodes.new('ShaderNodeBackground')
            bsdf_node = slot.node_tree.nodes.get("BSDF") or slot.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
            mat_output = slot.node_tree.nodes.get('Material Output') or slot.node_tree.nodes.new('ShaderNodeOutputMaterial')
            
            bg_node.inputs['Color'].default_value = rusty_brown
            bsdf_node.inputs['Base Color'].default_value = rusty_brown
            bsdf_node.inputs['Roughness'].default_value = 0.45
            bsdf_node.inputs['Metallic'].default_value = 0.7
            
            slot.node_tree.links.new(bg_node.outputs['Background'], mat_output.inputs['Surface'])
        elif i == 3:
            slot.use_nodes = True
            bg_node = slot.node_tree.nodes.new('ShaderNodeBackground')
            bsdf_node = slot.node_tree.nodes.get("BSDF") or slot.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
            mat_output = slot.node_tree.nodes.get('Material Output') or slot.node_tree.nodes.new('ShaderNodeOutputMaterial')
            
            bg_node.inputs['Color'].default_value = olive_drab
            bsdf_node.inputs['Base Color'].default_value = olive_drab
            bsdf_node.inputs['Roughness'].default_value = 0.75
            bsdf_node.inputs['Metallic'].default_value = 0.0
            
            slot.node_tree.links.new(bg_node.outputs['Background'], mat_output.inputs['Surface'])
    
    print("Materials assigned to mesh")
    
    # Export the textured mesh as a new file with embedded textures reference
    export_path = "/Users/Ori/Documents/Projects/BunkerGame/assets/generated_meshes/military_bunk_bed_textured.blend"
    bpy.ops.wm.save_as_mainfile(filepath=export_path)
    print(f"Saved Blender project: {export_path}")
    
    # Create a texture manifest file for Rojo integration
    manifest_content = f"""# Bunker Bed Texture Manifest
# Generated by Blender automation script

## Materials Created:
- Bunk_Bed_Mat_0: Dark metallic frame (dark gray, high metallic)
- Bunk_Bed_Mat_1: Dark blue fabric bedding
- Bunk_Bed_Mat_2: Rusty brown metal accents
- Bunk_Bed_Mat_3: Olive drab military fabric

## Color Palette:
- Dark Gray Frame: {dark_gray[0]:.2f}, {dark_gray[1]:.2f}, {dark_gray[2]:.2f}
- Dark Blue Fabric: {dark_blue[0]:.2f}, {dark_blue[1]:.2f}, {dark_blue[2]:.2f}
- Rusty Brown Accents: {rusty_brown[0]:.2f}, {rusty_brown[1]:.2f}, {rusty_brown[2]:.2f}
- Olive Drab Fabric: {olive_drab[0]:.2f}, {olive_drab[1]:.2f}, {olive_drab[2]:.2f}

## Aesthetic Notes:
- Dark, industrial bunker aesthetic
- Metallic accents on frame and trim
- Military-grade fabric textures
- Weathered/rusty metal details for authenticity
"""
    
    manifest_path = "/Users/Ori/Documents/Projects/BunkerGame/assets/textures/bunk_bed/MATERIAL_MANIFEST.txt"
    with open(manifest_path, 'w') as f:
        f.write(manifest_content)
    print(f"Created material manifest: {manifest_path}")

print("Texture job completed successfully!")
print("Blender project saved and textures created.")
