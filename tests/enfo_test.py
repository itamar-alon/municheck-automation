from pathlib import Path
import sys
from sys import path
from selenium import webdriver
import time

# --- Path Fixes ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets
# וודא שהשם כאן תואם לשם הקובץ שיצרת (למשל pages.enforcement_page)
from pages.enfo_page import EnforcementPage 

# --- Loading Configuration ---
secrets = load_secrets()

if secrets:
    ENFORCEMENT_URL = secrets.get('enforcement_url')
    
    if not ENFORCEMENT_URL:
        print("❌ Error: Missing 'enforcement_url' in secrets.json")
        sys.exit(1)
    
    # --- Running the Test ---
    try:
        print("Starting Enforcement Interface Test")
        driver = webdriver.Chrome() 
        driver.maximize_window()
        
        with driver:
            print("✅ Driver initialized successfully.")
            
            # --- Step A: Setup Page ---
            enforcement_page = EnforcementPage(driver, ENFORCEMENT_URL) 
            enforcement_page.open_enforcement_page() 
            
            # --- Step B: Title Validation ---
            page_title = enforcement_page.get_page_title()
            if "פיקוח" in page_title or "Enforcement" in page_title:
                 print(f"✅ Page title verified: {page_title}") 
            else:
                 print(f"⚠️ Warning: Title might be different. Got: {page_title}")

            # --- Step C: Run Fast Link Tests ---
            enforcement_page.run_tab_1_external_link_tests() 
            
            print("\n>>> Enforcement page test finished successfully!") 
            
    except Exception as e:
        print(f"\n❌ TEST STOPPED: {e}")
        if 'driver' in locals():
             time.sleep(5)
else:
    print("Error: Could not load secrets data.")