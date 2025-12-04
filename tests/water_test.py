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
from pages.water_page import WaterPage  # 🟢 עדכון: Page Object חדש למים 


# --- 2. טעינה והגדרות ---
secrets = load_secrets()

if secrets:
    # ⬅️ Fetch required URL
    WATER_URL = secrets['water_url'] # 🟢 עדכון: משתמש ב-URL של ממשק המים
    
    # --- 3. הרצת הבדיקה (הלוגיקה המינימלית) ---
    try:
        # ⬅️ Step A: Perform Setup and Login
        driver = setup_driver_and_login(secrets)
        
        with driver: # Manages automatic driver closure
            print("✅ Setup and Login successful. Starting Water interface test.") # 🟢 עדכון שם הבדיקה
            
            # --- Step B: Test the Water Page ---
            # 🟢 עדכון: יצירת אובייקט WaterPage
            water_page = WaterPage(driver, WATER_URL) 
            water_page.open_water_page() # 🟢 עדכון שם המתודה
            
            # ⬅️ Title Validation
            page_title = water_page.get_page_title() # 🟢 עדכון שם האובייקט
            
            # 🟢 עדכון: אימות כותרת רלוונטית למים/ברזים (כנראה 'מים' או 'Water')
            assert "מים" in page_title or "Water" in page_title, "❌ Page title validation failed! Title not related to Water."
            print(f"✅ Water page title validation successful: {page_title}") # 🟢 עדכון שם הבדיקה
            
            
            # --- Step C: Run all navigation and link tests ---
            
            # 1. Test Tab 1 (Default: Hydrants/Usage)
            # 🟢 עדכון: מתודת בדיקת לינקים המתאימה לממשק מים
            water_page.run_tab_1_external_link_tests() 
            water_page.navigate_to_tab_2()
            water_page.run_tab_2_external_link_tests()
            water_page.navigate_to_tab_3()
            water_page.run_tab_3_external_link_tests()
            
            print("\n>>> Water interface test finished successfully!") # 🟢 עדכון שם הבדיקה
            
    except Exception as e:
        print(f"❌ The test failed! Error occurred: {e}")
        
else:
    print("Cannot proceed without login credentials.")