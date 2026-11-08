#!/usr/bin/env python3
"""
Industrial Infrastructure Generator for Bunker Game
Creates electrical conduits, pipes, ventilation ducts, drainage elements,
service panels, brackets, and storage systems.
"""

import os
import math

def create_conduit_mesh(output_path, length=100, diameter=5):
    """Create an electrical conduit mesh (cylindrical tube)"""
    lines = []
    
    # Create a cylindrical conduit with multiple segments for detail
    num_segments = 32
    radius = diameter / 2
    
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        x = length * (i / num_segments) - length/2
        y = radius * math.cos(angle)
        z = radius * math.sin(angle)
        
        lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    # Create faces for the cylinder (simplified)
    num_faces = num_segments - 1
    for i in range(num_faces):
        angle1 = 2 * math.pi * i / num_segments
        angle2 = 2 * math.pi * (i + 1) / num_segments
        
        x1, y1, z1 = length/2, radius * math.cos(angle1), radius * math.sin(angle1)
        x2, y2, z2 = length/2 - 0.5, radius * math.cos(angle1), radius * math.sin(angle1)
        x3, y3, z3 = length/2 - 0.5, radius * math.cos(angle2), radius * math.sin(angle2)
        
        lines.append(f"f {num_segments + i + 1} {i + 1} {i + 2}")
    
    with open(output_path, 'w') as f:
        f.write("# Electrical Conduit Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_pipe_with_valve_mesh(output_path):
    """Create a pipe section with valve"""
    lines = []
    
    # Pipe body
    num_segments = 24
    radius = 3
    
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        x = (i - num_segments/2) * 0.5
        y = radius * math.cos(angle)
        z = radius * math.sin(angle)
        
        lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    # Pipe faces
    for i in range(num_segments - 1):
        angle1 = 2 * math.pi * i / num_segments
        angle2 = 2 * math.pi * (i + 1) / num_segments
        
        lines.append(f"f {num_segments + i + 1} {i + 1} {i + 2}")
    
    # Valve section (simplified as a protrusion)
    valve_x = -5
    for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4]:
        y_valve = radius * math.cos(angle) + 1.5
        z_valve = radius * math.sin(angle) + 1.5
        lines.append(f"v {valve_x:.4f} {y_valve:.4f} {z_valve:.4f}")
    
    # Valve faces
    for i in range(3):
        angle1 = i * math.pi/4
        angle2 = (i + 1) * math.pi/4
        lines.append(f"f {num_segments + 5 + i} {num_segments + 4} {num_segments + 5}")
    
    with open(output_path, 'w') as f:
        f.write("# Pipe with Valve Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_ventilation_duct_mesh(output_path):
    """Create a rectangular ventilation duct"""
    lines = []
    
    # Duct dimensions
    length = 100
    width = 40
    height = 30
    
    # Create the four sides of the rectangular duct
    for side in range(4):
        y_offset = (side % 2) * (height/2 - 5)
        z_offset = ((side + 1) % 2) * (width/2 - 5)
        
        # Generate vertices for this side
        num_segments = 16
        for i in range(num_segments + 1):
            angle = 2 * math.pi * i / num_segments
            x = length * (i / num_segments) - length/2
            y = height/2 - 5 + y_offset
            z = width/2 - 5 + z_offset
            
            lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    # Simplified faces for each side
    with open(output_path, 'w') as f:
        f.write("# Ventilation Duct Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_drainage_element_mesh(output_path):
    """Create a drainage pipe/grate element"""
    lines = []
    
    # Drainage grate (simplified)
    num_segments = 12
    radius = 8
    
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        x = length * (i / num_segments) - length/2 if 'length' in locals() else 0
        y = radius * math.cos(angle)
        z = radius * math.sin(angle)
        
        lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    with open(output_path, 'w') as f:
        f.write("# Drainage Element Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_service_panel_mesh(output_path):
    """Create a service panel box"""
    lines = []
    
    # Panel dimensions (width, height, depth)
    w, h, d = 20, 30, 5
    
    # Front face vertices
    for y in [h/2 - 1, h/2 + 1]:
        for z in [-d/2, d/2]:
            lines.append(f"v {w/2:.4f} {y:.4f} {z:.4f}")
            lines.append(f"v {-w/2:.4f} {y:.4f} {z:.4f}")
    
    with open(output_path, 'w') as f:
        f.write("# Service Panel Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_bracket_mesh(output_path):
    """Create a mounting bracket"""
    lines = []
    
    # L-shaped bracket
    lines.append("v 0.0 0.0 0.0")
    lines.append("v 15.0 0.0 0.0")
    lines.append("v 15.0 10.0 0.0")
    lines.append("v 0.0 10.0 0.0")
    lines.append("v 0.0 10.0 -3.0")
    lines.append("v 15.0 10.0 -3.0")
    
    with open(output_path, 'w') as f:
        f.write("# Bracket Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_storage_rack_mesh(output_path):
    """Create a storage rack/shelf unit"""
    lines = []
    
    # Rack dimensions
    w, h, d = 40, 60, 15
    
    # Main frame vertices
    for x in [w/2, -w/2]:
        for y in [-h/2 + 2, h/2 - 2]:
            lines.append(f"v {x:.4f} {y:.4f} {d/2:.4f}")
            lines.append(f"v {x:.4f} {y:.4f} {-d/2:.4f}")
    
    with open(output_path, 'w') as f:
        f.write("# Storage Rack Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_emergency_equipment_mesh(output_path):
    """Create emergency equipment (fire extinguisher, etc.)"""
    lines = []
    
    # Cylinder shape for fire extinguisher
    radius = 4
    height = 25
    
    num_segments = 16
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        x = radius * math.cos(angle)
        y = height/2 - 5
        
        lines.append(f"v {x:.4f} {y:.4f} {radius * math.sin(angle):.4f}")
    
    with open(output_path, 'w') as f:
        f.write("# Emergency Equipment Mesh\n")
        for line in lines:
            f.write(line + '\n')

def main():
    output_dir = "/Users/Ori/Documents/Projects/BunkerGame/assets/generated_meshes"
    
    # Create electrical conduits (multiple along structural members)
    create_conduit_mesh(f"{output_dir}/electrical_conduit_01.obj", length=50, diameter=4)
    create_conduit_mesh(f"{output_dir}/electrical_conduit_02.obj", length=75, diameter=6)
    create_conduit_mesh(f"{output_dir}/electrical_conduit_03.obj", length=100, diameter=8)
    
    # Create pipes with valves and supports
    create_pipe_with_valve_mesh(f"{output_dir}/pipe_section_01.obj")
    create_pipe_with_valve_mesh(f"{output_dir}/pipe_section_02.obj")
    create_bracket_mesh(f"{output_dir}/pipe_support_bracket_01.obj")
    
    # Create ventilation ducts
    create_ventilation_duct_mesh(f"{output_dir}/ventilation_duct_main.obj")
    create_ventilation_duct_mesh(f"{output_dir}/ventilation_duct_branch.obj")
    
    # Create drainage elements
    create_drainage_element_mesh(f"{output_dir}/drainage_grate_01.obj")
    create_drainage_element_mesh(f"{output_dir}/drainage_pipe_section.obj")
    
    # Create service panels
    create_service_panel_mesh(f"{output_dir}/service_panel_main.obj")
    create_service_panel_mesh(f"{output_dir}/service_panel_auxiliary.obj")
    
    # Create brackets and supports
    create_bracket_mesh(f"{output_dir}/mounting_bracket_01.obj")
    create_bracket_mesh(f"{output_dir}/mounting_bracket_02.obj")
    create_storage_rack_mesh(f"{output_dir}/storage_rack_unit.obj")
    
    # Create emergency equipment
    create_emergency_equipment_mesh(f"{output_dir}/fire_extinguisher.obj")
    create_emergency_equipment_mesh(f"{output_dir}/emergency_light.obj")
    
    print("Industrial infrastructure meshes created successfully!")

if __name__ == "__main__":
    main()
