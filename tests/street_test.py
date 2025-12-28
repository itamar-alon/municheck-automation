from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path 
import sys 
from sys import path 
import time

# --- 1. Path Fix ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets 
from pages.street_page import StreetPage 

# --- 2. Loading and Configuration ---
secrets = load_secrets()

if secrets:
    STREET_URL = secrets['street_url']
    
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        with driver: 
            print("✅ Driver initialized successfully. Starting Street Info test.")
            
            street_page = StreetPage(driver, STREET_URL)
            street_page.open_street_page() 
            
            print(">>> Waiting for main page elements to load...")
            wait = WebDriverWait(driver, 10)
            
            try:
                # 1. Attempt to locate search box (Best indicator page is working)
                # Using selector for input field or "Street Name" text
                search_box_locator = (By.XPATH, "//input | //*[contains(text(), 'שם הרחוב')]")
                wait.until(EC.presence_of_element_located(search_box_locator))
                print("✅ Search component found on page.")
            except:
                # 2. If not found, check if redirected to login
                if "login" in driver.current_url.lower():
                    raise Exception("❌ Redirected to Login page. Authentication might be required to view street info.")
                else:
                    raise Exception("❌ Page loaded but Search field is missing. Content might be restricted.")

            # --- Step C: Run Data Verification Flow ---
            print(">>> Starting street search and data verification...")
            street_page.search_and_verify_table() 
            
            print(">>> Opening popup for extended data verification...")
            street_page.expand_and_verify_popup()
            
            print("\n>>> Street Info page test finished successfully!") 
            
    except Exception as e:
        print(f"❌ Test failed! An error occurred: {e}")
        
else:
    print("Cannot proceed without configuration data.")