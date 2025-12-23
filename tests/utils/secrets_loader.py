# secrets_loader.py

import json
from pathlib import Path

def load_secrets(file_name="secrets.json"):
    """
    Loads configuration data from a JSON file using an absolute path calculation.
    The code assumes that the secrets.json file is located in the project root,
    three levels above this file.
    """
    
    # 1. Determine the absolute path of the secrets_loader.py file
    script_path = Path(__file__).resolve() 
    
    # 2. Calculate the project root (move up from utils/ to tests/ and then to SELENIUM SCRIPTS/)
    # Since the file is in tests/utils/, we need to move up three levels.
    project_root = script_path.parent.parent.parent 
    
    # Note: Structure is SELENIUM SCRIPTS -> tests -> utils -> secrets_loader.py
    
    # 3. Build the full path to the secrets.json file
    file_path = project_root / file_name
    
    # Print the path being passed to open()
    print(f"*** Attempting to load data from absolute path: {file_path}") 
    
    try:
        # Opening the file
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File {file_path} not found. Ensure it is located in the project root.")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: File {file_path} is not in a valid JSON format. Ensure it is not empty.")
        return None

# --- Verification ---
if __name__ == '__main__':
    data = load_secrets()
    if data:
        print("\n✅ Secrets loading successful!")