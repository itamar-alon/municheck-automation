from selenium.webdriver.common.by import By
# ייבוא קלאס הבסיס שלך
from .base_page import BasePage 
# אין צורך לייבא כאן את WebDriverWait או EC!

class LoginPage(BasePage):
    """קלאס המייצג את דף הכניסה."""

    # --- Locators ---
    ID_FIELD = (By.NAME, "tz")
    PHONE_FIELD = (By.NAME, "phone")
    LOGIN_BUTTON_TEXT = "שלח לי קוד חד פעמי"
    LOGIN_BUTTON = (By.XPATH, f"//button[text()='{LOGIN_BUTTON_TEXT}']")
    OTP_FIELD = (By.NAME, "code") 
    
    def __init__(self, driver, url):
        # קורא ל-constructor של קלאס הבסיס
        super().__init__(driver)
        self.LOGIN_URL = url # שומר את ה-URL של דף הכניסה

    def enter_credentials(self, user_id: str, user_phone: str):
        """מנווט, מזין תעודת זהות ומספר טלפון ולוחץ על 'שלח לי קוד'."""
        
        self.go_to_url(self.LOGIN_URL) # שימוש במתודה מ-BasePage
        print(f">>> נווט ל: {self.LOGIN_URL}")
        
        # הזנת ת.ז.
        # ⬅️ תיקון: שימוש ב-get_element במקום wait_for_presence
        self.enter_text(self.ID_FIELD, user_id) 
        print(">>> הוזנה תעודת זהות")

        # הזנת טלפון
        self.enter_text(self.PHONE_FIELD, user_phone) # שימוש במתודה מ-BasePage
        print(">>> הוזן מספר טלפון")

        # לחיצה על כפתור
        self.click(self.LOGIN_BUTTON) # שימוש במתודה מ-BasePage
        print(f">>> בוצעה לחיצה על '{self.LOGIN_BUTTON_TEXT}' לאחר המתנה.")

    def wait_for_otp_and_login(self, home_url_part: str):
        """
        ממתין שהמשתמש יזין את קוד ה-OTP ויבצע ניווט.
        """
        
        # 1. ודא ששדה ה-OTP הופיע בדף
        # ⬅️ תיקון: שימוש ב-get_element במקום wait_for_presence
        self.get_element(self.OTP_FIELD) 
        print(">>> שדה קוד חד פעמי נמצא. ⏰ ממתין שתזין את הקוד בדפדפן ותלחץ 'התחברות'.")

        # 2. המתנה לניווט (היעלמות שדה ה-OTP)
        self.wait_for_invisibility(self.OTP_FIELD, timeout=60) # שימוש במתודה מ-BasePage
        print(">>> זוהה ניווט: שדה ה-OTP נעלם בהצלחה.")
        
        # 3. המתנה ל-URL הסופי
        self.wait_for_url_to_contain(home_url_part, timeout=20)
        print(f">>> בוצע ניווט מוצלח ל-URL המכיל '{home_url_part}'.")