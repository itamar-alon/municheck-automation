# tests/full_flow.py

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from pathlib import Path
import sys 
from sys import path 


# --- 1. Path Fix (Crucial for finding 'pages' directory) ---
project_root = Path(__file__).resolve().parent.parent 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
    print(f"*** Project root path added to sys.path: {project_root}")
    


# ⬅️ 2. Importing necessary modules
from tests.utils.secrets_loader import load_secrets 
from tests.test_setup import setup_driver_and_login
from pages.daycare_page import DaycarePage 
from pages.login_page import LoginPage 
from pages.business_page import BusinessLicensePage
from pages.enfo_page import EnforcementPage
from pages.street_page import StreetPage
from pages.water_page import WaterPage
from pages.parking_page import ParkingPage # 🟢 ייבוא ParkingPage

# --- 3. Loading Configuration and Settings ---
secrets = load_secrets() 

if secrets:
    # הגדרת משתני נתיב קצה-לקצה
    LOGIN_URL = secrets.get('login_url')
    HOME_URL_PART = secrets.get('home_url_part')
    DAYCARE_URL = secrets.get('daycare_url')
    BUSINESS_URL = secrets['business_url']
    ENFORCEMENT_URL = secrets['enforcement_url']
    STREET_URL = secrets['street_url']
    WATER_URL = secrets['water_url']
    PARKING_URL = secrets['parking_url'] # 🟢 טעינת URL של חניה

    # 🟢 טעינת פרטי המשתמש
    USER_ID = secrets.get('user_id')
    PASSWORD = secrets.get('password')

    driver = None 
    
    try:
        # ⬅️ 4. קריאה לפונקציית Setup (Login מתבצע כאן)
        driver = setup_driver_and_login(secrets)
        
        # ⬅️ 5. ניהול סגירה אוטומטית של הדרייבר באמצעות 'with'
        with driver:
            
            print("✅ Setup complete. Starting end-to-end test...") 
            
            # --- בדיקת דף Daycare ---
            # ... (הבדיקות הקודמות נשארות כפי שהן) ...

            # --- Starting Parking Interface Test ---
            print("\n" + "="*50)
            print("Starting Parking Interface page test")
            print("="*50)
            
            # 1. יצירת מופע חדש וניווט
            parking_page = ParkingPage(driver, PARKING_URL)
            parking_page.open_parking_page()
            
            # 2. אימות כותרת
            page_title = parking_page.get_page_title()
            assert "חניה" in page_title or "Parking" in page_title, "❌ Parking page title is incorrect!"
            print(f"✅ Parking page title validation successful: {page_title}")

            # 3. טאב 1 (ברירת מחדל): קישורים חיצוניים
            parking_page.run_tab_1_external_link_tests()
            
            # 4. טאב 2: בדיקת נתונים דינמיים (כולל Re-authentication)
            parking_page.navigate_to_tab_2()
            # 🟢 קריאה מתוקנת עם העברת פרטי המשתמש
            parking_page.search_and_verify_parking_data(USER_ID, PASSWORD) 
            
            # 5. טאב 3: קישורים חיצוניים
            parking_page.navigate_to_tab_3()
            parking_page.run_tab_3_external_link_tests()
            
            print("✅ Parking Interface page test finished successfully!") 
            
            # ... (הבדיקות האחרות) ...
            
            print("\n>>> End-to-end test finished successfully!") 
            
    except Exception as e:
        # ⬅️ טיפול שגיאות נקי
        print(f"❌ End-to-end test failed! Error occurred: {e}")
        
else:
    print("Cannot proceed without login credentials.")