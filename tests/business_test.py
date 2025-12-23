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
from pages.business_page import BusinessLicensePage 


# --- 2. Loading and Configuration ---
secrets = load_secrets()

if secrets:
    BUSINESS_URL = secrets['business_url']
    
    # --- 3. Running the Test ---
    try:
        # Initialize Driver directly
        driver = webdriver.Chrome() 
        driver.maximize_window()
        
        with driver: 
            print("✅ Driver initialized successfully. Navigating directly to Business License page.")
            
            # --- Step A: Open Business License Page ---
            business_page = BusinessLicensePage(driver, BUSINESS_URL)
            business_page.open_business_page()
            
            # Title Validation
            page_title = business_page.get_page_title()
            assert "רישוי" in page_title or "Business" in page_title, f"❌ Incorrect page title! Received: {page_title}"
            print(f"✅ Business page title validation passed: {page_title}")
            
            # --- Step B: Run Navigation and Link Tests ---
            
            # 1. Test Tab 1 (Default)
            business_page.run_tab_1_external_link_tests()
            
            # 2. Navigate and Test Tab 2 (Requirements)
            business_page.navigate_to_tab_2() 
            business_page.run_tab_2_external_link_tests()
            
            # 3. Navigate and Test Tab 3 (Forms)
            business_page.navigate_to_tab_3()
            business_page.run_tab_3_external_link_tests()
            
            print("\n>>> Business License page test completed successfully!")
            
    except Exception as e:
        print(f"❌ Test failed! An error occurred: {e}")
        
else:
    print("Error: Could not load secrets data (URL).")