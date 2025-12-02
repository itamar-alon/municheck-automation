from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from pathlib import Path 
import sys 
from sys import path 

# --- 1. תיקון נתיבים (השארת הבלוק נחוצה למציאת תיקיית 'pages') ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from .utils.secrets_loader import load_secrets 
from .test_setup import setup_driver_and_login 
from pages.enfo_page import EnforcementPage  # Enforcement Page Object 


# --- 2. טעינה והגדרות ---
secrets = load_secrets()

if secrets:
    # ⬅️ Fetch required URL
    ENFORCEMENT_URL = secrets['enforcement_url']
    
    # --- 3. הרצת הבדיקה (הלוגיקה המינימלית) ---
    try:
        # ⬅️ Step A: Perform Setup and Login
        driver = setup_driver_and_login(secrets)
        
        with driver: # Manages automatic driver closure
            print("✅ Setup and Login successful. Starting Enforcement test.")
            
            # --- Step B: Test the Enforcement Page ---
            enforcement_page = EnforcementPage(driver, ENFORCEMENT_URL) 
            enforcement_page.open_enforcement_page() 
            
            # ⬅️ Title Validation
            page_title = enforcement_page.get_page_title()
            assert "פיקוח" in page_title or "Enforcement" in page_title, "❌ Page title validation failed!"
            print(f"✅ Enforcement page title validation successful: {page_title}") 
            
            
            # --- Step C: Run all navigation and link tests ---
            
            # 1. Test Tab 1 (Default: Reports/Fines)
            enforcement_page.run_tab_1_external_link_tests() 
            
            print("\n>>> Enforcement page test finished successfully!") 
            
    except Exception as e:
        print(f"❌ The test failed! Error occurred: {e}")
        
else:
    print("Cannot proceed without login credentials.")