# tests/test_setup.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.login_page import LoginPage
from typing import Optional

def setup_driver_and_login(secrets: dict) -> Optional[webdriver.Chrome]:
    """
    מבצע אתחול לדרייבר, מבצע כניסה (Login) ומחזיר דרייבר מחובר.
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

    try:
        login_page = LoginPage(driver, LOGIN_URL)
        login_page.enter_credentials(secrets['user_data']['id_number'], 
                                     secrets['user_data']['phone_number'])
        
        # ממתין להשלמת ה-OTP והניווט לדף הבית
        login_page.wait_for_otp_and_login(HOME_URL_PART)
        
        print("✅ ה-Setup: כניסה בוצעה בהצלחה.")
        return driver
        
    except Exception as e:
        print(f"❌ ה-Setup נכשל במהלך ה-Login: {e}")
        driver.quit()
        # אם יש שגיאה ב-Setup, אנחנו לא יכולים להמשיך
        raise