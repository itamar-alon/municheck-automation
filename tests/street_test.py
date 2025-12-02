from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from pathlib import Path 
import sys 
from sys import path 

# --- 1. תיקון נתיבים ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from .utils.secrets_loader import load_secrets 
from .test_setup import setup_driver_and_login 
from pages.street_page import StreetPage  # ⬅️ ייבוא הקלאס StreetPage


# --- 2. טעינה והגדרות ---
secrets = load_secrets()

# ❌ הוסר: TEST_STREET_NAME מוגדר כעת בתוך קלאס StreetPage

if secrets:
    # ⬅️ שליפת ה-URL הנדרש
    STREET_URL = secrets['street_url']
    
    # --- 3. הרצת הבדיקה (הלוגיקה המינימלית) ---
    try:
        # ⬅️ Step A: Perform Setup and Login
        driver = setup_driver_and_login(secrets)
        
        with driver: # Manages automatic driver closure
            print("✅ Setup and Login successful. Starting Street Info test.")
            
            # --- Step B: Test the Street Info Page ---
            street_page = StreetPage(driver, STREET_URL) # ⬅️ יצירת מופע חדש
            street_page.open_street_page() 
            
            # ⬅️ Title Validation
            page_title = street_page.get_page_title()
            assert "רחוב" in page_title or "Street" in page_title, "❌ Page title validation failed!"
            print(f"✅ Street Info page title validation successful: {page_title}") 
            
            
            # --- Step C: Run the Data Validation Flow ---
            
            # 1. Search for a street and verify table data
            # 🟢 שינוי: קורא ללא ארגומנט, משתמש ב-StreetPage.TEST_STREET_NAME
            street_page.search_and_verify_table() 
            
            # 2. Click the plus icon and verify the popup data
            street_page.expand_and_verify_popup()
            
            print("\n>>> Street Info page test finished successfully!") 
            
    except Exception as e:
        print(f"❌ The test failed! Error occurred: {e}")
        
else:
    print("Cannot proceed without login credentials.")