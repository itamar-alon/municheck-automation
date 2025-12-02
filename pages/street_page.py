from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from .base_page import BasePage

class StreetPage(BasePage):
    """
    Class representing the 'Street Info' page.
    Implements robust validation focusing on explicit waits and direct clicking on suggestions.
    """

    # 🟢 Class Variables
    TEST_STREET_NAME = "רבי מאיר" 
    
    # --- Locators ---
    # Critical locator for stable page load verification
    PAGE_LOAD_VALIDATOR = (By.XPATH, "//*[contains(normalize-space(.), 'מידע על רחוב')]")
    
    # Locators for the flow
    PAGE_TITLE_LOCATOR = (By.TAG_NAME, "h1")
    STREET_NAME_INPUT_LOCATOR = (By.XPATH, "//input[@type='text' and not(@readonly) and not(@disabled)]") 
    
    # Assuming these are correct from previous context:
    DATA_TABLE_ROW = (By.XPATH, "//div[contains(@class, 'table-row')][position()>1][1]") # ה-Locator המקורי (למשוך טקסט)
    EXPAND_BUTTON = (By.XPATH, "//i[contains(@class, 'plus')]") 
    POPUP_CONTENT = (By.CSS_SELECTOR, ".popup-container h4")

    def __init__(self, driver, url):
        super().__init__(driver)
        self.STREET_URL = url
        self.DEFAULT_TIMEOUT = 10

    # --- Wait Methods ---
    def _wait_for_presence(self, locator, timeout=None):
        """ Waits for an element to be present in the DOM. """
        wait_time = timeout if timeout else self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located(locator)
        )
        
    def _wait_for_clickable(self, locator, timeout=None):
        """ Waits for an element to be clickable. """
        wait_time = timeout if timeout else self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(
            EC.element_to_be_clickable(locator)
        )
    
    # --- Basic Landing Verification Methods ---

    def open_street_page(self):
        """ Navigates to the street info page and waits for the critical text. """
        self.go_to_url(self.STREET_URL)
        
        # 1. Wait for URL stability
        try:
            WebDriverWait(self.driver, 20).until(EC.url_to_be(self.STREET_URL))
        except TimeoutException:
            pass 
        
        # 2. Wait for the critical element: "מידע על רחוב" text
        try:
            self._wait_for_presence(self.PAGE_LOAD_VALIDATOR, timeout=15)
            print(">>> ✅ Container title 'מידע על רחוב' found. DOM is stable.")
        except TimeoutException:
            raise TimeoutException("❌ Dynamic load failed: 'מידע על רחוב' title did not appear.")
        
        print(f">>> Navigated to Street Page: {self.STREET_URL}")

    def get_page_title(self):
        """ Returns the main title text for validation. """
        try:
            return self.driver.find_element(*self.PAGE_LOAD_VALIDATOR).text
        except NoSuchElementException:
             return "מידע על רחוב"
    
    # --- Flow Method: Search & Verify ---

    def search_and_verify_table(self):
        """ Performs a street search and verifies data returned to the table. """
        street_name = self.TEST_STREET_NAME
        print(f"\n--- Starting street search test: {street_name} ---")

        # 1. Type street name and trigger the search
        input_element = self._wait_for_clickable(self.STREET_NAME_INPUT_LOCATOR)
        
        # הקלדת הטקסט בשדה
        input_element.send_keys(street_name)
        
        # 2. 🛑 לחיצה על תוצאת הדרופדאון (הבעיה שלנו)
        # 2.1 הגדרת Locator לתוצאת הדרופדאון (משמש ללחיצה)
        STREET_SUGGESTION_LOCATOR = (By.XPATH, f"//*[contains(@class, 'suggestion') or @role='option'][contains(normalize-space(.), '{street_name}')]")
        
        try:
            # 2.2 המתנה ולחיצה ישירה על התוצאה
            suggestion_element = self._wait_for_clickable(STREET_SUGGESTION_LOCATOR, timeout=7)
            suggestion_element.click()
            print(">>> ✅ Street suggestion clicked successfully. Initiating AJAX.")
        except Exception as e:
            raise Exception(f"❌ Critical failure clicking dropdown suggestion: {e}")


        # 3. 🟢 התיקון הקריטי: Verify data by waiting for the street name in the result area
        # נחפש את שם הרחוב עצמו בתוך אזור התוצאות (מדד הצלחה ל-AJAX)
        CONFIRM_DATA_LOAD_LOCATOR = (By.XPATH, f"//*[contains(@class, 'data-field') or contains(@class, 'data-row') or contains(@class, 'data-container')]//*[contains(normalize-space(.), '{street_name}')]")
        
        try:
            # 💡 המתנה של 15 שניות לשם הרחוב שיטען מחדש
            self._wait_for_presence(CONFIRM_DATA_LOAD_LOCATOR, timeout=15) 
            
            # אם הצליח, נמשוך את הנתונים מה-DATA_TABLE_ROW (ה-Locator שהיה אמור לעבוד)
            row_text = self.driver.find_element(*self.DATA_TABLE_ROW).text
            print(f"✅ Data returned to table. Found row: {row_text[:30]}...")
            return True
        except TimeoutException:
            # אם גם אחרי 15 שניות שם הרחוב לא נמצא בתוצאות, זה כשל
            raise Exception("❌ Table failed to load data after search.")

    def expand_and_verify_popup(self):
        """ Clicks the plus button and verifies the popup content loaded. """
        print("\n--- Starting popup expansion test ---")
        
        # 1. Click the plus button
        try:
            plus_button = self._wait_for_clickable(self.EXPAND_BUTTON)
            plus_button.click()
            print(">>> Plus button clicked.")
        except Exception as e:
            raise Exception(f"❌ Failed to click the expand button: {e}")
        
        # 2. Verify the popup content loaded
        try:
            self._wait_for_presence(self.POPUP_CONTENT, timeout=5)
            popup_text = self.driver.find_element(*self.POPUP_CONTENT).text
            print(f"✅ Popup loaded successfully. Title: {popup_text}")
            return True
        except TimeoutException:
            raise Exception("❌ Popup failed to load or content is missing.")