from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from .base_page import BasePage 
from selenium.common.exceptions import TimeoutException # נשמר הייבוא

class LoginPage(BasePage):
    """קלאס המייצג את דף הכניסה, כעת תומך בלוגין באמצעות סיסמה."""

    # --- Locators ---
    PASSWORD_TAB_TEXT = "באמצעות סיסמה"
    PASSWORD_TAB = (By.XPATH, f"//button[text()='{PASSWORD_TAB_TEXT}']")
    
    # 🛑 תיקון: Locator רחב יותר (מחפש לפי name, type, או attributes שונים)
    ID_FIELD = (By.XPATH, "//input[@name='identityNumber' or @name='tz' or @type='text' or @type='number']") 
    PASSWORD_FIELD = (By.NAME, "password") 
    
    FINAL_LOGIN_BUTTON_TEXT = "כניסה"
    FINAL_LOGIN_BUTTON = (By.XPATH, f"//button[text()='{FINAL_LOGIN_BUTTON_TEXT}']")
    
    OVERLAY_LOCATOR = (By.CSS_SELECTOR, ".MuiDialog-container[role='presentation']")


    def __init__(self, driver, url):
        super().__init__(driver) 
        self.LOGIN_URL = url 

    def login_with_password(self, user_id: str, user_password: str):
        """מבצע לוגין מלא באמצעות תעודת זהות וסיסמה."""
        
        self.go_to_url(self.LOGIN_URL)
        print(f">>> נווט ל: {self.LOGIN_URL}")
        
        # 1. לחיצה על טאב "באמצעות סיסמה"
        self.click(self.PASSWORD_TAB)
        print(f">>> בוצעה לחיצה על טאב '{self.PASSWORD_TAB_TEXT}'.")

        # 🛑 תיקון קריטי: המתנה ששדה תעודת הזהות יהיה לחיץ (Clickable)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.ID_FIELD) # ⬅️ השתנה ל-Clickable
        )
        
        # 2. הזנת ת.ז.
        self.enter_text(self.ID_FIELD, user_id) 
        print(">>> הוזנה תעודת זהות")

        # 3. הזנת סיסמה
        self.enter_text(self.PASSWORD_FIELD, user_password)
        print(">>> הוזנה סיסמה")

        # 4. 🛑 לחיצה על כפתור כניסה סופי (עם טיפול ב-Overlay)
        try:
            # המתנה להיעלמות Overlay אם הופיע
            self.wait_for_invisibility(self.OVERLAY_LOCATOR, timeout=10)
        except TimeoutException:
            print(">>> אזהרה: Overlay לא נעלם, מנסה לחיצת כוח (JS).")

        # לחיצה באמצעות JavaScript כגיבוי
        login_button_element = self.wait_for_clickable_element(self.FINAL_LOGIN_BUTTON, timeout=5)
        self.execute_script("arguments[0].click();", login_button_element)
            
        print(f">>> בוצעה לחיצה על כפתור '{self.FINAL_LOGIN_BUTTON_TEXT}'.")

    def wait_for_successful_login(self, home_url_part: str):
        """ ממתין לניווט מוצלח לאחר הלוגין באמצעות סיסמה. """
        self.wait_for_url_to_contain(home_url_part, timeout=20)
        print(f">>> בוצע ניווט מוצלח ל-URL המכיל '{home_url_part}'.")