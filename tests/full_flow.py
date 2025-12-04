# tests/full_flow.py

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import sys 


# --- 1. הוספת שורש הפרויקט ל-PYTHONPATH (חיוני לייבוא) ---
project_root = Path(__file__).resolve().parent.parent 
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
    print(f"*** Project root path added to sys.path: {project_root}")
    


# ⬅️ 2. ייבוא המודולים הדרושים
from tests.utils.secrets_loader import load_secrets 
from tests.test_setup import setup_driver_and_login
from pages.daycare_page import DaycarePage 
from pages.login_page import LoginPage 
from pages.business_page import BusinessLicensePage
from pages.enfo_page import EnforcementPage
from pages.street_page import StreetPage
from pages.water_page import WaterPage

# --- 3. טעינת נתוני הקונפיגורציה ---
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

    driver = None 
    
    try:
        # ⬅️ 4. קריאה לפונקציית Setup (Login מתבצע כאן)
        driver = setup_driver_and_login(secrets)
        
        # ⬅️ 5. ניהול סגירה אוטומטית של הדרייבר באמצעות 'with'
        with driver:
            
            print("✅ Setup complete. Starting end-to-end test...")
            
            # --- בדיקת דף Daycare ---
            daycare_page = DaycarePage(driver, DAYCARE_URL)
            daycare_page.open_daycare_page()
            
            page_title = daycare_page.get_page_title()
            assert "צהרונים" in page_title or "Daycare" in page_title, "❌ Page title is incorrect!"
            print(f"✅ Daycare page title validation successful: {page_title}")
            
            daycare_page.run_tab_1_external_link_tests()
            daycare_page.navigate_to_daycare_tab()
            daycare_page.run_tab_2_external_link_tests()

# --- שלב ג': בדיקת דף רישוי עסקים (Business License) ---
            print("\n" + "="*50)
            print("Starting Business License page test")
            print("="*50)
            
            business_page = BusinessLicensePage(driver, BUSINESS_URL)
            business_page.open_business_page()
            
            page_title = business_page.get_page_title()
            assert "רישוי עסקים" in page_title, "❌ Business License page title is incorrect!"
            print(f"✅ Business License page title validation successful: {page_title}")

            business_page.run_tab_1_external_link_tests()
            business_page.navigate_to_tab_2()
            business_page.run_tab_2_external_link_tests()
            business_page.navigate_to_tab_3()
            business_page.run_tab_3_external_link_tests()
            
            print("✅ Business License page test finished successfully!")

            print("\n" + "="*50)
            print("Starting Enforcement page test")
            print("="*50)
            
            # ⬅️ שלב ב': בדיקת דף ה-Enforcement
            enforcement_page = EnforcementPage(driver, ENFORCEMENT_URL)
            enforcement_page.open_enforcement_page()
            
            # ⬅️ אימות הכותרת
            page_title = enforcement_page.get_page_title()
            assert "פיקוח" in page_title or "Enforcement" in page_title, "❌ Enforcement page title is incorrect!"
            print(f"✅ Enforcement page title validation successful: {page_title}")
            
            # ⬅️ שלב ג': הרצת כל שלבי הניווט והבדיקה
            enforcement_page.run_tab_1_external_link_tests()
            
            
            print("\n>>> Enforcement page test finished successfully!")


            print("\n" + "="*50)
            print("Starting Street Info page test")
            print("="*50)
            
            # 1. יצירת מופע חדש וניווט
            street_page = StreetPage(driver, STREET_URL)
            street_page.open_street_page()

            # 2. אימות כותרת הדף
            page_title = street_page.get_page_title()
            assert "רחוב" in page_title or "Street" in page_title, "❌ Street page title validation failed!"
            print(f"✅ Street Info page title validation successful: {page_title}")

            # 3. הרצת הפלואו החדש: חיפוש, אימות טבלה ואימות פופ-אפ
            street_page.search_and_verify_table()
            street_page.expand_and_verify_popup()

            print("\n>>> Street Info page test finished successfully!")
            
            
            # 🟢 ⬅️ שלב ג': בדיקת ממשק המים (Water Interface) 
            print("\n" + "="*50)
            print("Starting Water Interface page test")
            print("="*50)
            
            water_page = WaterPage(driver, WATER_URL)
            water_page.open_water_page()
            
            page_title = water_page.get_page_title()
            assert "מים" in page_title or "Water" in page_title, "❌ Water page title is incorrect!"
            print(f"✅ Water page title validation successful: {page_title}")

            water_page.run_tab_1_external_link_tests()
            water_page.navigate_to_tab_2()
            water_page.run_tab_2_external_link_tests()
            water_page.navigate_to_tab_3()
            water_page.run_tab_3_external_link_tests()
            
            print("✅ Water Interface page test finished successfully!")






            print("\n>>> End-to-end test finished successfully!")
            
    except Exception as e:
        # ⬅️ טיפול שגיאות נקי
        print(f"❌ End-to-end test failed! Error occurred: {e}")
        
else:
    print("Cannot proceed without configuration data.")