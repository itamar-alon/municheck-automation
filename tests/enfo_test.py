from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from pathlib import Path 
import sys 
from sys import path 

# --- 1. Path Fixes ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from .utils.secrets_loader import load_secrets 
# setup_driver_and_login removed as it is no longer needed
from pages.enfo_page import EnforcementPage 


# --- 2. Loading and Configuration ---
secrets = load_secrets()

if secrets:
    # Fetch required URL
    ENFORCEMENT_URL = secrets['enforcement_url']
    
    # --- 3. Running the Test ---
    try:
        # Direct driver initialization without login
        driver = webdriver.Chrome() 
        driver.maximize_window()
        
        with driver: # Automatic driver closure
            print("✅ Driver initialized successfully. Navigating to Enforcement page.")
            
            # --- Step A: Setup Enforcement Page ---
            enforcement_page = EnforcementPage(driver, ENFORCEMENT_URL) 
            enforcement_page.open_enforcement_page() 
            
            # --- Step B: Title Validation ---
            page_title = enforcement_page.get_page_title()
            assert "פיקוח" in page_title or "Enforcement" in page_title, f"❌ Incorrect page title! Received: {page_title}"
            print(f"✅ Enforcement page title validation passed: {page_title}") 
            
            # --- Step C: Run Link Tests ---
            # (Make sure to update EnforcementPage to use the Fast Check method as well)
            print(">>> Starting link tests for Enforcement page...")
            enforcement_page.run_tab_1_external_link_tests() 
            
            print("\n>>> Enforcement page test finished successfully!") 
            
    except Exception as e:
        print(f"❌ Test failed! An error occurred: {e}")
        
else:
    print("Error: Could not load secrets data (URL).")