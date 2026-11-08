#!/usr/bin/env python3
"""
Python script to generate the Luau crate interaction service.
Creates a Lua file for managing crate interactions in BunkerGame.
"""

import os

# Define paths
SCRIPT_DIR = "/Users/Ori/Documents/Projects/BunkerGame"
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "src", "ServerScriptService", "Game", "Services", "CrateInteractionService.luau")

def generate_crate_service():
    """Generate the Luau crate interaction service content."""
    
    luau_content = '''-- Crate Interaction Service for BunkerGame
-- Manages old_military_ammo_crate_01 and looted crates

local CrateInteractionService = {}

-- Initialize lootedCrates table to track all looted crates
CrateInteractionService.lootedCrates = {
    [1] = {
        crateId = "old_military_ammo_crate_01",
        name = "Old Military Ammo Crate 01",
        status = "active",
        lootCount = 0,
        lastLooted = nil
    }
}

-- Function to manage old_military_ammo_crate_01
function CrateInteractionService.manageAmmoCrate(crateId)
    local crateData = CrateInteractionService.lootedCrates[1]
    
    if crateId == "old_military_ammo_crate_01" then
        print("Managing ammo crate: " .. crateData.name)
        return true
    else
        warn("Unknown crate ID: " .. crateId)
        return false
    end
end

-- Function to handle ProximityPrompt Triggered event
function CrateInteractionService.onProximityPromptTriggered(prompt, player)
    local crate = prompt.Parent
    
    if crate and crate:IsA("Model") then
        print("Player " .. player.Name .. " triggered proximity on crate: " .. crate.Name)
        
        -- Check if this is the ammo crate
        for _, lootData in ipairs(CrateInteractionService.lootedCrates) do
            if lootData.crateId == "old_military_ammo_crate_01" then
                lootData.lootCount = lootData.lootCount + 1
                lootData.lastLooted = tick()
                print("Ammo crate looted. Total loots: " .. lootData.lootCount)
            end
        end
        
        -- Reset proximity prompt after interaction
        if prompt then
            prompt.Triggered:Connect(function()
                CrateInteractionService.onProximityPromptTriggered(prompt, player)
            end)
        end
    end
end

-- Initialize the service
print("Crate Interaction Service initialized")
print("Tracking lootedCrates table with " .. #CrateInteractionService.lootedCrates .. " entries")

return CrateInteractionService
'''
    
    return luau_content


def main():
    """Main function to create and write the crate interaction service."""
    
    print(f"Creating crate interaction service at: {OUTPUT_FILE}")
    
    # Generate the Luau content
    luau_content = generate_crate_service()
    
    # Write the file
    with open(OUTPUT_FILE, 'w') as f:
        f.write(luau_content)
    
    print(f"Successfully created: {OUTPUT_FILE}")
    print("Contents written:")
    print("- old_military_ammo_crate_01 management")
    print("- lootedCrates table initialization")
    print("- ProximityPrompt Triggered event handling")
    
    # Verify file exists
    if os.path.exists(OUTPUT_FILE):
        print(f"\nVerification: File exists at {OUTPUT_FILE}")
        return True
    else:
        print(f"Error: File was not created at {OUTPUT_FILE}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
