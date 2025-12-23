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
from pages.water_page import WaterPage 


# --- 2. Loading and Configuration ---
secrets = load_secrets()

if secrets:
    # Fetch required URL
    WATER_URL = secrets['water_url']
    
    # --- 3. Running the Test ---
    try:
        # Direct driver initialization without login
        driver = webdriver.Chrome() 
        driver.maximize_window()
        
        with driver: # Manages automatic driver closure
            print("✅ Driver initialized successfully. Starting Water interface test.")
            
            # --- Step A: Setup Water Page ---
            water_page = WaterPage(driver, WATER_URL) 
            water_page.open_water_page()
            
            # --- Step B: Title Validation ---
            page_title = water_page.get_page_title()
            assert "מים" in page_title or "Water" in page_title, f"❌ Page title validation failed! Received: {page_title}"
            print(f"✅ Water page title validation successful: {page_title}")
            
            # --- Step C: Run All Navigation and Link Tests ---
            
            # 1. Test Tab 1 (Default)
            print(">>> Running tests for Tab 1...")
            water_page.run_tab_1_external_link_tests() 
            
            # 2. Test Tab 2
            water_page.navigate_to_tab_2()
            print(">>> Running tests for Tab 2...")
            water_page.run_tab_2_external_link_tests()
            
            # 3. Test Tab 3
            water_page.navigate_to_tab_3()
            print(">>> Running tests for Tab 3...")
            water_page.run_tab_3_external_link_tests()
            
            print("\n>>> Water interface test finished successfully!")
            
    except Exception as e:
        print(f"❌ The test failed! Error occurred: {e}")
        
else:
    print("Error: Could not load secrets data (URL).")