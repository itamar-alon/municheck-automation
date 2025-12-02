# tests/test_setup.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage
from typing import Optional
import time # ⬅️ חובה לייבא את time לייצוב

def setup_driver_and_login(secrets: dict) -> Optional[webdriver.Chrome]:
    """
    מבצע אתחול לדרייבר, מבצע כניסה (Login) ומחזיר דרייבר מחובר,
    כעת באמצעות תעודת זהות וסיסמה.
    """
    
    # 1. הגדרות הדרייבר
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 2. אתחול
    driver = webdriver.Chrome(options=chrome_options)

    # 3. ביצוע Login
    LOGIN_URL = secrets.get('login_url')
    HOME_URL_PART = secrets.get('home_url_part')

    # 🟢 שליפת הנתונים המעודכנים (תעודת זהות וסיסמה)
    try:
        user_id = secrets['user_data']['id_number']
        # הנחה שהמפתח 'password' נוסף לקטע 'user_data' ב-secrets.json
        user_password = secrets['user_data']['password'] 
    except KeyError as e:
        print(f"❌ שגיאת הגדרת סודות: חסר המפתח הנדרש {e} ב-secrets.json. ודא שהמפתח 'password' קיים.")
        driver.quit()
        raise

    try:
        login_page = LoginPage(driver, LOGIN_URL)
        
        # 🟢 ייצוב: המתנה קשיחה קצרה לאחר יצירת המופע כדי לוודא טעינה מלאה
        time.sleep(1)
        
        # ⬅️ קריאה למתודת הלוגין החדשה (login_with_password)
        login_page.login_with_password(user_id, user_password)
        
        # ⬅️ קריאה למתודת ההמתנה החדשה (wait_for_successful_login)
        login_page.wait_for_successful_login(HOME_URL_PART)
        
        print("✅ ה-Setup: כניסה בוצעה בהצלחה.")
        return driver
        
    except Exception as e:
        print(f"❌ ה-Setup נכשל במהלך ה-Login: {e}")
        driver.quit()
        # אם יש שגיאה ב-Setup, אנחנו לא יכולים להמשיך
        raise