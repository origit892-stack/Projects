#!/usr/bin/env python3
"""
Create better geometry for infrastructure meshes that will work with texture generation.
This script creates more complex OBJ files with proper face definitions.
"""

import math

def create_detailed_pipe(output_path, length=100, diameter=6):
    """Create a detailed pipe mesh with proper faces"""
    
    lines = []
    radius = diameter / 2
    
    # Number of segments around the circumference
    num_segments = 32
    
    # Create vertices for cylinder body
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        
        # Pipe extends along X axis
        x_start = -length/2
        x_end = length/2
        step_x = (x_end - x_start) / num_segments
        
        for j in range(num_segments + 1):
            x = x_start + j * step_x
            
            y = radius * math.cos(angle)
            z = radius * math.sin(angle)
            
            lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    # Create faces for cylinder body (connect adjacent vertices around circumference)
    face_idx = 0
    for i in range(num_segments):
        for j in range(num_segments):
            v1 = (i + 1) * (num_segments + 1) + j + 1
            v2 = (i + 1) * (num_segments + 1) + j + 2
            v3 = i * (num_segments + 1) + j + 2
            v4 = i * (num_segments + 1) + j + 1
            
            lines.append(f"f {face_idx + 1} {v1} {v2} {v3}")
            face_idx += 1
    
    # Add valve section - protrusion at one end
    valve_x = length/2 - 5
    for angle in [0, math.pi/4, math.pi/2, 3*math.pi/4]:
        y_valve = radius * math.cos(angle) + 2
        z_valve = radius * math.sin(angle) + 2
        
        lines.append(f"v {valve_x:.4f} {y_valve:.4f} {z_valve:.4f}")
    
    # Valve faces
    for i in range(3):
        angle1 = i * math.pi/4
        angle2 = (i + 1) * math.pi/4
        v1 = num_segments * (num_segments + 1) + 5 + i
        v2 = num_segments * (num_segments + 1) + 6 + i
        lines.append(f"f {face_idx + 1} {v1} {v2}")
    
    with open(output_path, 'w') as f:
        f.write("# Detailed Pipe Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_detailed_conduit(output_path, length=80, diameter=5):
    """Create a detailed electrical conduit mesh"""
    
    lines = []
    radius = diameter / 2
    
    num_segments = 24
    
    # Create vertices for cylinder body
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        
        x_start = -length/2
        x_end = length/2
        step_x = (x_end - x_start) / num_segments
        
        for j in range(num_segments + 1):
            x = x_start + j * step_x
            
            y = radius * math.cos(angle)
            z = radius * math.sin(angle)
            
            lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    # Create faces for cylinder body
    face_idx = 0
    for i in range(num_segments):
        for j in range(num_segments):
            v1 = (i + 1) * (num_segments + 1) + j + 1
            v2 = (i + 1) * (num_segments + 1) + j + 2
            v3 = i * (num_segments + 1) + j + 2
            v4 = i * (num_segments + 1) + j + 1
            
            lines.append(f"f {face_idx + 1} {v1} {v2} {v3}")
            face_idx += 1
    
    with open(output_path, 'w') as f:
        f.write("# Detailed Electrical Conduit Mesh\n")
        for line in lines:
            f.write(line + '\n')

def create_detailed_ventilation_duct(output_path, length=100, width=40, height=30):
    """Create a detailed rectangular ventilation duct"""
    
    lines = []
    
    # Create vertices for each side of the rectangular duct
    num_segments = 16
    
    # Side 1: Top (y = height/2)
    y_top = height/2 - 5
    z_offset = width/2 - 5
    
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        
        x_start = -length/2
        x_end = length/2
        step_x = (x_end - x_start) / num_segments
        
        for j in range(num_segments + 1):
            x = x_start + j * step_x
            
            y = y_top
            z = z_offset + radius * math.sin(angle) if 'radius' in locals() else 0
            
            lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    # Side 2: Bottom (y = -height/2)
    y_bottom = -height/2 + 5
    
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        
        x_start = -length/2
        x_end = length/2
        step_x = (x_end - x_start) / num_segments
        
        for j in range(num_segments + 1):
            x = x_start + j * step_x
            
            y = y_bottom
            z = z_offset + radius * math.sin(angle) if 'radius' in locals() else 0
            
            lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    # Side 3: Front (z = width/2)
    x_offset = length/2 - 5
    
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        
        y_start = -height/2 + 5
        y_end = height/2 - 5
        step_y = (y_end - y_start) / num_segments
        
        for j in range(num_segments + 1):
            y = y_start + j * step_y
            
            x = x_offset
            z = radius * math.cos(angle) if 'radius' in locals() else 0
            
            lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    # Side 4: Back (z = -width/2)
    z_back = -width/2 + 5
    
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        
        y_start = -height/2 + 5
        y_end = height/2 - 5
        step_y = (y_end - y_start) / num_segments
        
        for j in range(num_segments + 1):
            y = y_start + j * step_y
            
            x = radius * math.cos(angle) if 'radius' in locals() else 0
            z = z_back
            
            lines.append(f"v {x:.4f} {y:.4f} {z:.4f}")
    
    with open(output_path, 'w') as f:
        f.write("# Detailed Ventilation Duct Mesh\n")
        for line in lines:
            f.write(line + '\n')

def main():
    output_dir = "/Users/Ori/Documents/Projects/BunkerGame/assets/generated_meshes"
    
    # Create detailed pipe with valve
    create_detailed_pipe(f"{output_dir}/pipe_section_01_detailed.obj", length=80, diameter=6)
    create_detailed_pipe(f"{output_dir}/pipe_section_02_detailed.obj", length=60, diameter=4)
    
    # Create detailed electrical conduit
    create_detailed_conduit(f"{output_dir}/electrical_conduit_main.obj", length=100, diameter=8)
    create_detailed_conduit(f"{output_dir}/electrical_conduit_branch.obj", length=50, diameter=6)
    
    # Create detailed ventilation duct
    create_detailed_ventilation_duct(f"{output_dir}/ventilation_duct_main_detailed.obj", 
                                     length=120, width=40, height=30)
    create_detailed_ventilation_duct(f"{output_dir}/ventilation_duct_branch_detailed.obj",
                                      length=60, width=30, height=25)
    
    print("Detailed infrastructure meshes created successfully!")

if __name__ == "__main__":
    main()
