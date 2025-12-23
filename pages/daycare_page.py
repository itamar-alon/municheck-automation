from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage 

class DaycarePage(BasePage):
    """Daycare page class, fixed for shortened URLs."""

    # --- Locators and Test Data ---
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    
    TAMAT_URL_PART = "CategoryID=3506"
    TAMAT_BUTTON_LOCATOR = (By.CSS_SELECTOR, f"a[href*='{TAMAT_URL_PART}']") 
    
    TAB_BUTTON_NAME = "מעונות יום" 
    TAB_2_URL_PART = "?tab=1" 

    # ⬅️ Updated with the shortened URLs found in your log
    TAB_1_EXTERNAL_LINKS = {
        "איזור אישי": "rb.gy/cewz20",
        "רישום לצהרוני בית הספר": "rb.gy/cewz20",
    }
    
    TAB_2_EXTERNAL_LINKS = {
        "אזור אישי": "PrivateArea", 
        "רישום מעונות יום": "AnotherProcIsRunning",
        "רישום מעון חרצית": "CategoryID=3506"
    }

    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.DAYCARE_URL = url 

    def open_daycare_page(self):
        self.go_to_url(self.DAYCARE_URL)
        print(f">>> Navigated to Daycare page: {self.DAYCARE_URL}")

    def get_page_title(self):
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    def _verify_link_href_fast(self, link_text, expected_url_part):
        print(f"--- Checking link: {link_text} ---")
        
        if "חרצית" in link_text:
            dynamic_locator = self.TAMAT_BUTTON_LOCATOR
        else:
            # Using a more robust XPath for Hebrew text
            dynamic_locator = (By.XPATH, f"//a[contains(., '{link_text}')]")
        
        try:
            link_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(dynamic_locator)
            )
            actual_url = link_element.get_attribute("href")
            
            if expected_url_part in actual_url:
                print(f"✅ Fast Check Passed: '{link_text}' points to correct URL.")
                return True
            else:
                print(f"❌ Validation Failed: Expected '{expected_url_part}' but found '{actual_url}'")
                return False
        except Exception:
            print(f"❌ Could not find link: '{link_text}'")
            return False

    def run_tab_1_external_link_tests(self):
        print("\n--- Starting Fast Link Check (Tab 1 - Default) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_link_href_fast(link_name, url_part)

    def navigate_to_daycare_tab(self):
        """ Switches to the second tab. """
        target_url = self.DAYCARE_URL + self.TAB_2_URL_PART
        self.go_to_url(target_url) 
        print(f"\n>>> Navigating to Tab 2: {target_url}")
        time.sleep(2) 

    def run_tab_2_external_link_tests(self):
        print(f"\n--- Starting Fast Link Check (Tab 2: {self.TAB_BUTTON_NAME}) ---")
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_link_href_fast(link_name, url_part)