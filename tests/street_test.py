from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path 
import sys 
from sys import path 
import time

# --- 1. תיקון נתיבים ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from .utils.secrets_loader import load_secrets 
from pages.street_page import StreetPage 

# --- 2. טעינה והגדרות ---
secrets = load_secrets()

if secrets:
    STREET_URL = secrets['street_url']
    
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        with driver: 
            print("✅ הדרייבר עלה בהצלחה. מתחיל בדיקת Street Info.")
            
            street_page = StreetPage(driver, STREET_URL)
            street_page.open_street_page() 
            
            print(">>> ממתין לטעינת רכיבי הדף המרכזיים...")
            wait = WebDriverWait(driver, 10)
            
            try:
                # 1. ניסיון לאתר את תיבת החיפוש (זה האימות הכי טוב שהדף עובד)
                # נשתמש ב-Selector שמתאים לשדה קלט או לטקסט "שם הרחוב"
                search_box_locator = (By.XPATH, "//input | //*[contains(text(), 'שם הרחוב')]")
                wait.until(EC.presence_of_element_located(search_box_locator))
                print("✅ רכיב החיפוש אותר בדף.")
            except:
                # 2. אם לא מצאנו, נבדוק אם אנחנו בעצם בדף הלוגין
                if "login" in driver.current_url.lower():
                    raise Exception("❌ האתר הפנה אותנו לדף ההתחברות. כנראה שחייבים Login כדי לראות מידע על רחובות.")
                else:
                    raise Exception("❌ הדף נטען אך שדה החיפוש לא הופיע. ייתכן והתוכן חסום לאורחים.")

            # --- שלב ג': הרצת זרימת אימות הנתונים ---
            print(">>> מתחיל חיפוש רחוב ואימות נתונים...")
            street_page.search_and_verify_table() 
            
            print(">>> פותח פופ-אפ לאימות נתונים מורחב...")
            street_page.expand_and_verify_popup()
            
            print("\n>>> בדיקת דף Street Info הסתיימה בהצלחה!") 
            
    except Exception as e:
        print(f"❌ הבדיקה נכשלה! אירעה שגיאה: {e}")
        
else:
    print("לא ניתן להמשיך ללא נתוני כניסה.")