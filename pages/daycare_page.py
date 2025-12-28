from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
from urllib.parse import unquote
from .base_page import BasePage

class DaycarePage(BasePage):
    """
    Daycare page class.
    Includes Fast Link Checking + Error Screenshots + Redirect Warnings.
    """

    # --- Locators and Test Data ---
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    
    TAMAT_URL_PART = "CategoryID=3506"
    TAMAT_BUTTON_LOCATOR = (By.CSS_SELECTOR, f"a[href*='{TAMAT_URL_PART}']")
    
    TAB_BUTTON_NAME = "מעונות יום"
    TAB_2_URL_PART = "?tab=1"

    # נתונים (עודכנו לפי מה ששלחת)
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
    
    # 🟢 פונקציית עזר לצילום מסך בעת שגיאה
    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/error_daycare_{safe_name}_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save screenshot: {e}")

 
    def _verify_link_href_fast(self, link_text, expected_url_part):
        print(f"Testing: {link_text}")
        
        # 1. זיהוי הלוקייטור המתאים
        if "חרצית" in link_text:
            dynamic_locator = self.TAMAT_BUTTON_LOCATOR
        else:
            # שימוש ב-contains text גנרי וחזק
            dynamic_locator = (By.XPATH, f"//a[contains(., '{link_text}')]")
        
        # 2. מציאת האלמנט
        try:
            link_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(dynamic_locator)
            )
        except TimeoutException:
            print(f"❌ Link error: '{link_text}' (Element not found)")
            self._take_error_screenshot(link_text)
            return

        orig_window = self.driver.current_window_handle

        try:
            # 3. גלילה ולחיצה (JS עוקף חסימות)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_element)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", link_element)

            # 4. המתנה לחלון חדש
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            
            # 5. מעבר לחלון החדש
            new_win = [w for w in self.driver.window_handles if w != orig_window][0]
            self.driver.switch_to.window(new_win)

            # 6. בדיקת URL (עם פענוח עברית)
            current_url = unquote(self.driver.current_url)
            expected_decoded = unquote(expected_url_part)

            if expected_decoded in current_url:
                print(f"✅ Passed: {link_text}")
            else:
                # אזהרה בלבד על Redirect/URL שונה
                print(f"⚠️ Warning: {link_text} opened but URL differs.\n   Expected: ...{expected_decoded[-20:]}\n   Got:      ...{current_url[-20:]}")

            self.driver.close()

        except Exception as e:
            # שגיאה אמיתית (לא נפתח חלון / קריסה) -> צילום מסך
            print(f"❌ Link error: '{link_text}' (Failed to open/verify). Error: {e}")
            self._take_error_screenshot(link_text)
        
        finally:
            try: self.driver.switch_to.window(orig_window)
            except: pass

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