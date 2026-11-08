#!/usr/bin/env python3
"""
Script to write 'Write access confirmed!' to nexus_test.txt with proper error handling.
"""

import os


def write_to_file(filepath, content):
    """
    Write content to a file with proper error handling.
    
    Args:
        filepath (str): Path to the file to write to
        content (str): Content to write
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if directory exists
        directory = os.path.dirname(filepath)
        if not directory or not os.path.exists(directory):
            print(f"Error: Directory does not exist: {directory}")
            return False
        
        # Write to file in write mode (creates file if it doesn't exist, overwrites if it does)
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"Successfully wrote content to: {filepath}")
        return True
    
    except PermissionError:
        print(f"Error: Permission denied when writing to {filepath}")
        return False
    except IOError as e:
        print(f"IO Error occurred: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return False


def verify_file(filepath, expected_content):
    """
    Verify that the file exists and contains the expected content.
    
    Args:
        filepath (str): Path to the file to verify
        expected_content (str): Expected content in the file
    
    Returns:
        bool: True if verification successful, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Error: File does not exist: {filepath}")
            return False
        
        # Read and verify content
        with open(filepath, 'r') as f:
            actual_content = f.read()
        
        if actual_content == expected_content:
            print(f"Verification successful! Content matches.")
            return True
        else:
            print(f"Error: Content mismatch. Expected:\n{expected_content}\nActual:\n{actual_content}")
            return False
    
    except Exception as e:
        print(f"Error during verification: {type(e).__name__}: {e}")
        return False


def main():
    """Main function to execute the file write and verify operation."""
    
    # Define paths
    workspace_root = "/Users/Ori/Documents/Projects/BunkerGame"
    target_file = os.path.join(workspace_root, "nexus_test.txt")
    expected_content = "Write access confirmed!"
    
    print("=" * 60)
    print("File Write and Verify Script")
    print("=" * 60)
    print(f"\nTarget file: {target_file}")
    print(f"Expected content: '{expected_content}'\n")
    
    # Step 1: Write to file with error handling
    print("-" * 40)
    print("Step 1: Writing to file...")
    write_success = write_to_file(target_file, expected_content)
    
    if not write_success:
        print("\nFile write failed. Exiting.")
        return False
    
    # Step 2: Verify the file was created correctly
    print("-" * 40)
    print("Step 2: Verifying file content...")
    verify_success = verify_file(target_file, expected_content)
    
    if not verify_success:
        print("\nFile verification failed. Exiting.")
        return False
    
    # Success message
    print("-" * 40)
    print("SUCCESS: File created and verified correctly!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
