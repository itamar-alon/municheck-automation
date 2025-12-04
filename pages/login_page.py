from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from .base_page import BasePage 
from selenium.common.exceptions import TimeoutException # Imported exception retained

class LoginPage(BasePage):
    """Class representing the Login page, now supporting password login."""

    # --- Locators ---
    PASSWORD_TAB_TEXT = "באמצעות סיסמה"
    PASSWORD_TAB = (By.XPATH, f"//button[text()='{PASSWORD_TAB_TEXT}']")
    
    # 🛑 Fix: Wider Locator (searches by name, type, or various attributes)
    ID_FIELD = (By.XPATH, "//input[@name='identityNumber' or @name='tz' or @type='text' or @type='number']") 
    PASSWORD_FIELD = (By.NAME, "password") 
    
    FINAL_LOGIN_BUTTON_TEXT = "כניסה"
    FINAL_LOGIN_BUTTON = (By.XPATH, f"//button[text()='{FINAL_LOGIN_BUTTON_TEXT}']")
    
    OVERLAY_LOCATOR = (By.CSS_SELECTOR, ".MuiDialog-container[role='presentation']")


    def __init__(self, driver, url):
        super().__init__(driver) 
        self.LOGIN_URL = url 

    def login_with_password(self, user_id: str, user_password: str):
        """Performs a complete login using ID number and password."""
        
        self.go_to_url(self.LOGIN_URL)
        print(f">>> Navigated to: {self.LOGIN_URL}")
        
        # 1. Clicking the "Password" tab
        self.click(self.PASSWORD_TAB)
        print(f">>> Clicked on tab '{self.PASSWORD_TAB_TEXT}'.")

        # 🛑 Critical Fix: Wait for the ID field to be Clickable
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.ID_FIELD)
        )
        
        # 2. Entering ID
        self.enter_text(self.ID_FIELD, user_id) 
        print(">>> Entered ID number")

        # 3. Entering password
        self.enter_text(self.PASSWORD_FIELD, user_password)
        print(">>> Entered password")

        # 4. 🛑 Clicking the final login button (with Overlay handling)
        try:
            # Wait for Overlay to disappear if it appeared
            self.wait_for_invisibility(self.OVERLAY_LOCATOR, timeout=10)
        except TimeoutException:
            print(">>> Warning: Overlay did not disappear, attempting force click (JS).")

        # Clicking using JavaScript as fallback
        login_button_element = self.wait_for_clickable_element(self.FINAL_LOGIN_BUTTON, timeout=5)
        self.execute_script("arguments[0].click();", login_button_element)
            
        print(f">>> Clicked on button '{self.FINAL_LOGIN_BUTTON_TEXT}'.")

    def wait_for_successful_login(self, home_url_part: str):
        """ Waits for successful navigation after password login. """
        self.wait_for_url_to_contain(home_url_part, timeout=20)
        print(f">>> Successful navigation to URL containing '{home_url_part}'.")