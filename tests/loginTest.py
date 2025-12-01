from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import json
from pathlib import Path 
from utils.secrets_loader import load_secrets
# ⬅️ ייבוא ה-Page Object שלנו
from pages.login_page import LoginPage 

# --- 1. פונקציה לקריאת נתונים (ללא שינוי, תקינה) ---
def load_secrets(file_name="secrets.json"):
    """טוענת את נתוני התצורה מקובץ JSON באמצעות נתיב מוחלט."""
    
    script_path = Path(__file__).resolve() 
    project_root = script_path.parent.parent 
    file_path = project_root / file_name
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"*** מנסה לטעון נתונים מנתיב מוחלט: {file_path}") 
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ שגיאה: קובץ {file_path} לא נמצא.")
        return None
    except json.JSONDecodeError:
        print(f"❌ שגיאה: קובץ {file_path} אינו בפורמט JSON תקין.")
        return None


# --- 2. טעינה והגדרות ---
secrets = load_secrets()

if secrets:
    # שליפת נתוני כניסה ותצורה
    USER_ID = secrets['user_data']['id_number']
    USER_PHONE = secrets['user_data']['phone_number']
    LOGIN_URL = secrets['login_url']
    HOME_URL_PART = secrets['home_url_part'] 
    
    # --- 3. אתחול ה-WebDriver והרצת הבדיקה ---
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage") 
    
    # ה-driver.quit() מטופל אוטומטית על ידי ה-with
    try:
        with webdriver.Chrome(options=chrome_options) as driver:
            
            # 1. אתחול ה-Page Object!
            login_page = LoginPage(driver, LOGIN_URL)
            
            # 2. הרצת שלב 1: הזנת פרטים ולחיצה
            login_page.enter_credentials(USER_ID, USER_PHONE)
            
            # 3. הרצת שלב 2: המתנה ל-OTP וניווט
            login_page.wait_for_otp_and_login(HOME_URL_PART)

            print("✅ התחברות אושרה. הדפדפן נסגר אוטומטית.")

    except TimeoutException:
        # ⬅️ טיפול ב-Timeout
        print(f"❌ הבדיקה נכשלה! פג זמן ההמתנה (60 שניות ל-OTP או 20 שניות ל-URL).")
        try:
            current_url = driver.current_url
            print(f"  הכתובת הנוכחית היא: {current_url}")
        except:
            print(f"  אירעה שגיאת חיבור בעת ניסיון קבלת ה-URL. הדרייבר כנראה נסגר.")
        
    except Exception as e:
        # ⬅️ טיפול כללי
        print(f"❌ הבדיקה נכשלה! אירעה שגיאה בלתי צפויה: {e}")
        try:
            # ודא סגירה במקרה של שגיאה בלתי צפויה
            driver.quit()
        except:
            pass
        
    print(">>> הסקריפט הסתיים.")

else:
    print("לא ניתן להמשיך ללא נתוני כניסה.")