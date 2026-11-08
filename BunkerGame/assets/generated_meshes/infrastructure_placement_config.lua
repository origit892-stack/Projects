-- Industrial Infrastructure Placement Configuration for Bunker Game
-- This file defines the logical placement of all infrastructure components

return {
    -- Electrical Conduits (placed along structural members)
    electrical_conduits = {
        {
            name = "main_power_conduit",
            mesh = "electrical_conduit_03.obj",
            position = {x = 0, y = 2.5, z = -10},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "structural_beam_main",
            purpose = "Main power distribution along primary structural beam"
        },
        {
            name = "secondary_conduit_north",
            mesh = "electrical_conduit_02.obj",
            position = {x = -15, y = 3.0, z = -5},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "concrete_barricade_north",
            purpose = "Secondary power run to northern sector"
        },
        {
            name = "secondary_conduit_south",
            mesh = "electrical_conduit_01.obj",
            position = {x = 15, y = 3.0, z = -8},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "concrete_barricade_south",
            purpose = "Secondary power run to southern sector"
        }
    },

    -- Junction Boxes (near entry/exit points)
    junction_boxes = {
        {
            name = "main_junction_box",
            mesh = "service_panel_main.obj",
            position = {x = 0, y = 1.5, z = -20},
            rotation = {pitch = 0, yaw = 0, roll = 0},
            parent = "reinforced_steel_bunker_door",
            purpose = "Main junction box near primary entrance"
        },
        {
            name = "auxiliary_junction_box",
            mesh = "service_panel_auxiliary.obj",
            position = {x = -25, y = 1.5, z = -15},
            rotation = {pitch = 0, yaw = 0, roll = 0},
            parent = "stone_tunnel_entrance_archway",
            purpose = "Auxiliary junction box at tunnel entrance"
        }
    },

    -- Pipes with Valves and Supports (along walls)
    pipes = {
        {
            name = "water_supply_main",
            mesh = "pipe_section_01.obj",
            position = {x = -20, y = 4.5, z = -10},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "wall_north_wall",
            purpose = "Main water supply along north wall"
        },
        {
            name = "water_supply_branch_1",
            mesh = "pipe_section_02.obj",
            position = {x = -25, y = 4.5, z = -5},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "wall_north_wall",
            purpose = "Branch water line to utility area"
        },
        {
            name = "drainage_pipe_main",
            mesh = "pipe_section_02.obj",
            position = {x = -15, y = 1.0, z = -15},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "wall_south_wall",
            purpose = "Main drainage pipe along south wall"
        }
    },

    -- Pipe Supports and Brackets
    supports = {
        {
            name = "pipe_support_north_1",
            mesh = "pipe_support_bracket_01.obj",
            position = {x = -20, y = 4.5, z = -8},
            rotation = {pitch = 90, yaw = 0, roll = 0},
            parent = "concrete_barricade_north",
            purpose = "Support for water supply main"
        },
        {
            name = "pipe_support_south_1",
            mesh = "mounting_bracket_01.obj",
            position = {x = -15, y = 1.0, z = -12},
            rotation = {pitch = 90, yaw = 0, roll = 0},
            parent = "concrete_barricade_south",
            purpose = "Support for drainage pipe"
        },
        {
            name = "ventilation_support_1",
            mesh = "mounting_bracket_02.obj",
            position = {x = 0, y = 5.0, z = -10},
            rotation = {pitch = 90, yaw = 0, roll = 0},
            parent = "ceiling_structure",
            purpose = "Support for ventilation duct"
        }
    },

    -- Ventilation Ducts (aligned with airflow needs)
    ventilation_ducts = {
        {
            name = "main_ventilation_duct",
            mesh = "ventilation_duct_main.obj",
            position = {x = 0, y = 5.5, z = -15},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "industrial_metal_air_vent",
            purpose = "Main ventilation duct from exterior intake"
        },
        {
            name = "branch_ventilation_duct_north",
            mesh = "ventilation_duct_branch.obj",
            position = {x = -20, y = 5.5, z = -8},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "main_ventilation_duct",
            purpose = "Branch duct to northern utility area"
        },
        {
            name = "branch_ventilation_duct_south",
            mesh = "ventilation_duct_branch.obj",
            position = {x = 20, y = 5.5, z = -8},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "main_ventilation_duct",
            purpose = "Branch duct to southern utility area"
        }
    },

    -- Drainage Elements (in appropriate drainage paths)
    drainage_elements = {
        {
            name = "floor_grate_main",
            mesh = "drainage_grate_01.obj",
            position = {x = 0, y = -0.5, z = -25},
            rotation = {pitch = 0, yaw = 0, roll = 0},
            parent = "floor_main_drain",
            purpose = "Main floor drainage grate"
        },
        {
            name = "wall_drain_grate",
            mesh = "drainage_grate_01.obj",
            position = {x = -25, y = 0.5, z = -20},
            rotation = {pitch = 90, yaw = 0, roll = 0},
            parent = "wall_south_wall",
            purpose = "Wall-mounted drainage grate"
        },
        {
            name = "drainage_pipe_section_1",
            mesh = "drainage_pipe_section.obj",
            position = {x = -25, y = 0.5, z = -18},
            rotation = {pitch = 90, yaw = 0, roll = 0},
            parent = "wall_south_wall",
            purpose = "Drainage pipe section connecting to main drain"
        }
    },

    -- Machinery Components (in utility areas)
    machinery = {
        {
            name = "power_generator",
            mesh = "old_power_generator.obj",
            position = {x = -30, y = 1.2, z = -5},
            rotation = {pitch = 0, yaw = 0, roll = 0},
            parent = "utility_zone_floor",
            purpose = "Main power generator in utility area"
        }
    },

    -- Service Panels (near control points)
    service_panels = {
        {
            name = "main_control_panel",
            mesh = "service_panel_main.obj",
            position = {x = 0, y = 1.5, z = -22},
            rotation = {pitch = 0, yaw = 0, roll = 0},
            parent = "control_center_wall",
            purpose = "Main control panel at command center"
        },
        {
            name = "emergency_shutdown_panel",
            mesh = "service_panel_auxiliary.obj",
            position = {x = -25, y = 1.5, z = -18},
            rotation = {pitch = 0, yaw = 0, roll = 0},
            parent = "tunnel_entrance_wall",
            purpose = "Emergency shutdown panel at tunnel entrance"
        }
    },

    -- Brackets and Supports (sturdy installation)
    brackets = {
        {
            name = "ceiling_mount_bracket",
            mesh = "mounting_bracket_02.obj",
            position = {x = 0, y = 5.8, z = -12},
            rotation = {pitch = 90, yaw = 0, roll = 0},
            parent = "ceiling_main_beam",
            purpose = "Ceiling mount for overhead equipment"
        },
        {
            name = "wall_mount_bracket_1",
            mesh = "mounting_bracket_01.obj",
            position = {x = -25, y = 3.5, z = -15},
            rotation = {pitch = 90, yaw = 0, roll = 0},
            parent = "wall_north_wall",
            purpose = "Wall mount for equipment rack"
        }
    },

    -- Emergency Equipment (near exits/controls)
    emergency_equipment = {
        {
            name = "fire_extinguisher_1",
            mesh = "fire_extinguisher.obj",
            position = {x = -25, y = 1.0, z = -22},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "exit_wall_north",
            purpose = "Fire extinguisher near main exit"
        },
        {
            name = "fire_extinguisher_2",
            mesh = "fire_extinguisher.obj",
            position = {x = 25, y = 1.0, z = -22},
            rotation = {pitch = 0, yaw = -90, roll = 0},
            parent = "exit_wall_south",
            purpose = "Fire extinguisher near secondary exit"
        },
        {
            name = "emergency_light_1",
            mesh = "emergency_light.obj",
            position = {x = 0, y = 4.5, z = -20},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "ceiling_center",
            purpose = "Emergency lighting for evacuation route"
        }
    },

    -- Storage Systems (in utility zones)
    storage_systems = {
        {
            name = "main_storage_rack",
            mesh = "storage_rack_unit.obj",
            position = {x = -30, y = 1.5, z = -8},
            rotation = {pitch = 0, yaw = 90, roll = 0},
            parent = "utility_zone_wall",
            purpose = "Main storage rack in utility area"
        },
        {
            name = "barrel_storage_1",
            mesh = "rusty_metal_barrel.obj",
            position = {x = -32, y = 0.5, z = -8},
            rotation = {pitch = 0, yaw = 0, roll = 0},
            parent = "utility_zone_floor",
            purpose = "Bulk material storage barrel"
        },
        {
            name = "barrel_storage_2",
            mesh = "rusty_metal_barrel.obj",
            position = {x = -35, y = 0.5, z = -8},
            rotation = {pitch = 0, yaw = 180, roll = 0},
            parent = "utility_zone_floor",
            purpose = "Bulk material storage barrel"
        }
    },

    -- Existing Textured Meshes (already textured)
    existing_structures = {
        concrete_barricade_obj = "assets/generated_meshes/concrete_barricade.obj",
        industrial_metal_air_vent_obj = "assets/generated_meshes/industrial_metal_air_vent.obj",
        reinforced_steel_bunker_door_obj = "assets/generated_meshes/reinforced_steel_bunker_door.obj",
        rusty_metal_barrel_obj = "assets/generated_meshes/rusty_metal_barrel.obj"
    }
}
