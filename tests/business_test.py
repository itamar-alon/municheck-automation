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
from pages.business_page import BusinessLicensePage 


# --- 2. טעינה והגדרות ---
secrets = load_secrets()

if secrets:
    # ⬅️ שליפת ה-URL הדרושים בלבד
    BUSINESS_URL = secrets['business_url']
    
    # --- 3. הרצת הבדיקה (הלוגיקה המינימלית) ---
    try:
        # ⬅️ שלב א': ביצוע Setup ו-Login
        driver = setup_driver_and_login(secrets)
        
        with driver: # ניהול סגירה אוטומטית של הדרייבר
            print("✅ ה-Setup וה-Login בוצעו בהצלחה. מתחיל בדיקת רישוי עסקים.")
            
            # --- שלב ב': בדיקת דף ה-Business License ---
            business_page = BusinessLicensePage(driver, BUSINESS_URL)
            business_page.open_business_page()
            
            # ⬅️ אימות הכותרת
            page_title = business_page.get_page_title()
            assert "רישוי" in page_title or "Business" in page_title, "❌ כותרת הדף אינה נכונה!"
            print(f"✅ אימות כותרת דף buisness עבר בהצלחה: {page_title}")
            
            
            # --- שלב ג': הרצת כל שלבי הניווט והבדיקה ---
            
            # 1. בדיקת טאב 1 (ברירת מחדל)
            business_page.run_tab_1_external_link_tests()
            
            # 2. ניווט ובדיקת טאב 2 (דרישות ותנאים)
            business_page.navigate_to_tab_2() 
            business_page.run_tab_2_external_link_tests()
            
            # 3. ניווט ובדיקת טאב 3 (טפסים)
            business_page.navigate_to_tab_3()
            business_page.run_tab_3_external_link_tests()
            
            print("\n>>> בדיקת דף רישוי עסקים הסתיימה בהצלחה!")
            
    except Exception as e:
        print(f"❌ הבדיקה נכשלה! אירעה שגיאה: {e}")
        
else:
    print("לא ניתן להמשיך ללא נתוני כניסה.")




