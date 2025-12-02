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
    print(f"*** נתיב השורש הוסף ל-sys.path: {project_root}")
    


# ⬅️ 2. ייבוא המודולים הדרושים
from tests.utils.secrets_loader import load_secrets 
from tests.test_setup import setup_driver_and_login
from pages.daycare_page import DaycarePage 
from pages.login_page import LoginPage 
from pages.business_page import BusinessLicensePage
from pages.enfo_page import EnforcementPage
from pages.street_page import StreetPage

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

    driver = None 
    
    try:
        # ⬅️ 4. קריאה לפונקציית Setup (Login מתבצע כאן)
        driver = setup_driver_and_login(secrets)
        
        # ⬅️ 5. ניהול סגירה אוטומטית של הדרייבר באמצעות 'with'
        with driver:
            
            print("✅ ה-Setup הסתיים בהצלחה. מתחיל בדיקת קצה-לקצה...")
            
            # --- בדיקת דף Daycare ---
            daycare_page = DaycarePage(driver, DAYCARE_URL)
            daycare_page.open_daycare_page()
            
            page_title = daycare_page.get_page_title()
            assert "צהרונים" in page_title or "Daycare" in page_title, "❌ כותרת הדף אינה נכונה!"
            print(f"✅ אימות כותרת דף Daycare עבר בהצלחה: {page_title}")
            
            daycare_page.run_tab_1_external_link_tests()
            daycare_page.navigate_to_daycare_tab()
            daycare_page.run_tab_2_external_link_tests()

# --- שלב ג': בדיקת דף רישוי עסקים (Business License) ---
            print("\n" + "="*50)
            print("מתחיל בדיקת דף רישוי עסקים (Business License)")
            print("="*50)
            
            business_page = BusinessLicensePage(driver, BUSINESS_URL)
            business_page.open_business_page()
            
            page_title = business_page.get_page_title()
            assert "רישוי עסקים" in page_title, "❌ כותרת דף רישוי עסקים אינה נכונה!"
            print(f"✅ אימות כותרת דף רישוי עסקים עבר בהצלחה: {page_title}")

            business_page.run_tab_1_external_link_tests()
            business_page.navigate_to_tab_2()
            business_page.run_tab_2_external_link_tests()
            business_page.navigate_to_tab_3()
            business_page.run_tab_3_external_link_tests()
            
            print("✅ בדיקת דף רישוי עסקים הסתיימה בהצלחה!")

            print("\n--- מתחיל בדיקת דף פיקוח עירוני (Enforcement) ---")
            
            # ⬅️ שלב ב': בדיקת דף ה-Enforcement
            enforcement_page = EnforcementPage(driver, ENFORCEMENT_URL)
            enforcement_page.open_enforcement_page()
            
            # ⬅️ אימות הכותרת
            page_title = enforcement_page.get_page_title()
            assert "פיקוח" in page_title or "Enforcement" in page_title, "❌ כותרת דף Enforcement אינה נכונה!"
            print(f"✅ אימות כותרת דף Enforcement עבר בהצלחה: {page_title}")
            
            # ⬅️ שלב ג': הרצת כל שלבי הניווט והבדיקה
            enforcement_page.run_tab_1_external_link_tests()
        
            
            print("\n>>> בדיקת דף פיקוח עירוני הסתיימה בהצלחה!") 


            print("\n--- מתחיל בדיקת דף מידע על רחוב (Street Info) ---")
            
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
            

            print("\n>>> בדיקת קצה-לקצה הסתיימה בהצלחה!")
            
    except Exception as e:
        # ⬅️ טיפול שגיאות נקי
        print(f"❌ בדיקת קצה-לקצה נכשלה! אירעה שגיאה: {e}")
        
else:
    print("לא ניתן להמשיך ללא נתוני קונפיגורציה.")