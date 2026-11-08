#!/usr/bin/env python3
"""
Inspect the Roblox 3D Assets Generator Hugging Face Space API
and report live API signature.

DISCOVERED LIVE API STRUCTURE:
4 Named endpoints:
  1. /check_input_image - validates input image, returns None
  2. /preprocess - removes background, returns processed_image
  3. /generate_mvs - generates multiview images, returns generated_multiviews  
  4. /make3d - converts to 3D model, returns (output_model_obj_format, output_model_glb_format)

Workflow: preprocess → generate_mvs → make3d (chained on backend)
Direct call to /make3d appears available but no documented parameters.
"""

from gradio_client import Client

def main():
    client = Client("ThomasSimonini/Roblox-3D-Assets-Generator-v1")
    
    info = client.view_api()
    
    print("=" * 80)
    print("LIVE API DISCOVERY RESULTS")
    print("=" * 80)
    print(f"\nSpace: ThomasSimonini/Roblox-3D-Assets-Generator-v1")
    print(f"API URL: {client.api_url}")
    
    # Parse the endpoints from view_api()
    lines = str(info).split('\n') if info else []
    
    print("\n--- API ENDPOINTS ---")
    for line in lines:
        if 'Named API endpoints' in line:
            num = line.split()[4]  # extract "4"
            print(f"Total endpoints: {num}")
        
        if 'predict(' in line or '/predict' in line:
            print(line)
            for endpoint in ['check_input_image', 'preprocess', 'generate_mvs', 'make3d']:
                if endpoint in line:
                    print(f"\n    ✓ Endpoint: /{endpoint}")
                    
    print("\n--- PARAMETER SIGNEDATURE ---")
    for line in lines:
        if 'Parameters:' in line:
            print(line)
        if '- [' or 'Path to a local file' in line:
            print(line.strip())
            
    print("\n--- RETURNS ---")
    for line in lines:
        if 'Returns:' in line:
            print(line)
        if 'Model3d' in line or 'output_model' in line.lower():
            print(line.strip())
    
    print("\n--- CLIENT CALL TEST ---")
    try:
        result = client.predict(
            None,  # input_image - we'll use an image later
            True,  # do_remove_background
            api_name="/preprocess"
        )
        print(f"/preprocess test: {result}")
    except Exception as e:
        print(f"/preprocess requires valid input: {e}")
    
    print("\n--- MAKE3D TEST ---")
    try:
        result = client.predict(
            None,  # Note: this likely won't work without prior processing
            api_name="/make3d"
        )
        print(f"/make3d test succeeded with no parameters: {result}")
    except Exception as e:
        print(f"/make3d requires state or input: {e}")

if __name__ == "__main__":
    main()
