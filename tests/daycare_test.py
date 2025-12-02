from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from pathlib import Path 
from sys import path 

# ⬅️ ייבוא Page Objects ו-Utilities
from .utils.secrets_loader import load_secrets 
from tests.test_setup import setup_driver_and_login # ⬅️ המתודה שתטפל ב-Login ו-Setup
from pages.daycare_page import DaycarePage


# --- 1. טעינה והגדרות ---
secrets = load_secrets()

if secrets:
    # ⬅️ שליפת ה-URL הדרושים בלבד
    DAYCARE_URL = secrets['daycare_url']
    
    # --- 2. הרצת הבדיקה (הלוגיקה המינימלית) ---
    try:
        # ⬅️ שלב א': ביצוע Setup ו-Login (קריאה אחת לפונקציה המרכזית)
        driver = setup_driver_and_login(secrets)
        
        with driver: # ניהול סגירה אוטומטית של הדרייבר
            print("✅ ה-Setup וה-Login בוצעו בהצלחה!")
            
            # --- שלב ב': בדיקת דף ה-Daycare ---
            daycare_page = DaycarePage(driver, DAYCARE_URL)
            daycare_page.open_daycare_page()
            
            # ⬅️ אימות הכותרת
            page_title = daycare_page.get_page_title()
            assert "צהרונים" in page_title or "Daycare" in page_title, "❌ כותרת הדף אינה נכונה!"
            print(f"✅ אימות כותרת דף Daycare עבר בהצלחה: {page_title}")
            
            # ⬅️ הרצת כל בדיקות הקישור
            daycare_page.run_tab_1_external_link_tests()
            
            # ⬅️ (אם רוצים להריץ רק את הטאב הראשון)
            
            print("\n>>> הבדיקה על דף Daycare הסתיימה בהצלחה!")
            
    except Exception as e:
        print(f"❌ הבדיקה נכשלה! אירעה שגיאה: {e}")
        
else:
    print("לא ניתן להמשיך ללא נתוני כניסה.")