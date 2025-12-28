from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
from urllib.parse import unquote
from .base_page import BasePage

class WaterPage(BasePage):
    """
    Water Interface Page Object.
    Optimized for FAST link checking + Error Screenshots.
    """

    # --- Locators ---
    PAGE_TITLE = (By.TAG_NAME, "h1")
    GENERIC_LINK_XPATH = "//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{}')]"
    
    # 🟢 לוקייטור לטאב השני (בדרך כלל נקרא "טפסים" או דומה)
    TAB_2_LOCATOR = (By.XPATH, "//button[contains(text(), 'טפסים')]")

    # --- Data ---
    
    # טאב 1 - קישורים כלליים
    DEFAULT_TAB_LINKS = {
        "תשלום חשבון מים": "manit"
    }

    # טאב 2 - טפסים להורדה
    TAB_2_LINKS = {
        "בקשה לביקור": "setvisit.pdf",
        "בקשה לקבלת": "מידע.pdf",
        "הוראה": "מונגש",
        "החלפת": "החלפת",
        "סניטרית": "סניטרית",
        "הנדרשים": "טופס",
        "כשרות": "קרמ.pdf"
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.WATER_URL = url

    def open_water_page(self):
        self.go_to_url(self.WATER_URL)
        print(f">>> Navigated to Water page: {self.WATER_URL}")

    def get_page_title(self):
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text

    # 🟢 צילום מסך בשגיאה
    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/error_water_{safe_name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save screenshot: {e}")

    # 🟢 בדיקה מהירה (HREF)
    def _verify_external_link(self, link_text, expected_url_part):
        print(f"Testing: {link_text}")
        
        locator = (By.XPATH, self.GENERIC_LINK_XPATH.format(link_text))
        
        try:
            el = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            print(f"❌ Link error: '{link_text}' (Element not found)")
            self._take_error_screenshot(link_text)
            return

        href = el.get_attribute("href")
        orig_window = self.driver.current_window_handle

        try:
            # בדיקה מהירה ללא לחיצה
            if href and "http" in href:
                decoded_href = unquote(href)
                decoded_expected = unquote(expected_url_part)
                
                if decoded_expected in decoded_href:
                    print(f"✅ Passed (HREF check): {link_text}")
                    return 

            # Fallback: לחיצה
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", el)

            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            
            new_win = [w for w in self.driver.window_handles if w != orig_window][0]
            self.driver.switch_to.window(new_win)

            current_url = unquote(self.driver.current_url)
            expected_decoded = unquote(expected_url_part)

            if expected_decoded in current_url:
                print(f"✅ Passed: {link_text}")
            else:
                print(f"⚠️ Warning: {link_text} opened but URL differs.\n   Expected: ...{expected_decoded[-20:]}\n   Got:      ...{current_url[-20:]}")

            self.driver.close()

        except Exception as e:
            print(f"❌ Link error: '{link_text}' (Failed to open/verify). Error: {e}")
            self._take_error_screenshot(link_text)
        
        finally:
            try: self.driver.switch_to.window(orig_window)
            except: pass

    # --- פונקציות הרצה ---

    # טאב 1
    def run_tab_1_external_link_tests(self):
        print("\n--- Starting Fast Link Check (Water - Tab 1) ---")
        for link_name, url_part in self.DEFAULT_TAB_LINKS.items():
            self._verify_external_link(link_name, url_part)

    # ניווט לטאב 2
    def navigate_to_tab_2(self):
        print("\n--- Navigating to Tab 2: טפסים ---")
        try:
            tab = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.TAB_2_LOCATOR))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", tab)
            print(">>> Switched to Tab 2.")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Failed to switch to Tab 2: {e}")
            self._take_error_screenshot("tab_2_switch_fail")

    # טאב 2
    def run_tab_2_external_link_tests(self):
        print("\n--- Starting Fast Link Check (Water - Tab 2) ---")
        for link_name, url_part in self.TAB_2_LINKS.items():
            self._verify_external_link(link_name, url_part)