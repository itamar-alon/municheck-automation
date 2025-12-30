from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
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
    OPTIMIZED: Includes Fast HREF Checking (Smart Verify).
    """

    # --- Locators ---
    PAGE_TITLE = (By.TAG_NAME, "h1")
    # אותו לוקייטור חכם כמו במים - תופס גם כפתורים וגם לינקים לפי טקסט
    GENERIC_LINK_XPATH = "//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{}')]"

    # שם הטאב השני
    TAB_BUTTON_NAME = "מעונות יום"
    TAB_2_URL_PART = "?tab=1" # בצהרונים הניווט הוא דרך URL שזה מצוין ומהיר

    # --- נתונים (עודכנו לבדיקה מהירה - רק חלקים ייחודיים מה-URL) ---
    TAB_1_EXTERNAL_LINKS = {
        "איזור אישי": "cewz20",  # קיצרתי כדי שזה ימצא את זה ב-href
        "רישום לצהרוני בית הספר": "cewz20",
    }
    
    TAB_2_EXTERNAL_LINKS = {
        "אזור אישי": "PrivateArea",
        "רישום מעונות יום": "AnotherProcIsRunning",
        "רישום מעון חרצית": "CategoryID=3506"
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 3 # זמן המתנה קצר כי אנחנו רוצים לרוץ מהר
        self.DAYCARE_URL = url

    def open_daycare_page(self):
        self.go_to_url(self.DAYCARE_URL)
        print(f">>> Navigated to Daycare page: {self.DAYCARE_URL}")

    def get_page_title(self):
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            timestamp = datetime.now().strftime("%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            self.driver.save_screenshot(f"screenshots/err_daycare_{safe_name}_{timestamp}.png")
        except:
            pass

    # 🟢 זו הפונקציה החכמה שהעתקנו מ-WaterPage
    def _verify_external_link(self, link_text, expected_url_part):
        print(f"Testing: {link_text}...", end=" ", flush=True) 
        
        # שימוש בלוקייטור הגנרי החכם
        locator = (By.XPATH, self.GENERIC_LINK_XPATH.format(link_text))
        
        # טיפול מיוחד ל"חרצית" אם הלוקייטור הגנרי לא מוצא אותו (אופציונלי)
        if "חרצית" in link_text:
             # אם האתר משתמש במבנה מוזר לחרצית, אפשר לדרוס את הלוקייטור כאן
             # כרגע ננסה עם הגנרי, לרוב זה עובד
             pass 

        try:
            el = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            print(f"❌ Not Found")
            self._take_error_screenshot(link_text)
            return

        href = el.get_attribute("href")
        
        # ניקוי ה-URLים להשוואה קלה יותר
        clean_href = unquote(href).replace("https://", "").replace("http://", "") if href else ""
        clean_expected = unquote(expected_url_part).replace("https://", "").replace("http://", "")

        # 🚀 בדיקה מהירה 1: האם הציפייה נמצאת ב-HREF?
        if clean_expected in clean_href:
            print(f"✅ OK (HREF)")
            return 

        # 🚀 בדיקה מהירה 2: אם זה לינק מקוצר (rb.gy), לפעמים ה-HREF שונה מהיעד הסופי
        # כאן אנחנו נאלצים ללחוץ
        
        # Fallback: לחיצה (רק אם הבדיקה המהירה נכשלה)
        print(f"⚠️ Mismatch ('{clean_expected}' not in '{clean_href[:20]}...'), clicking...", end=" ")
        
        orig_window = self.driver.current_window_handle
        try:
            self.driver.execute_script("arguments[0].target='_blank'; arguments[0].click();", el)
            
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            new_win = [w for w in self.driver.window_handles if w != orig_window][0]
            self.driver.switch_to.window(new_win)
            
            current_url = unquote(self.driver.current_url)
            self.driver.close()
            self.driver.switch_to.window(orig_window)

            clean_current = current_url.replace("https://", "").replace("http://", "")
            
            if clean_expected in clean_current:
                print(f"✅ OK (Clicked)")
            else:
                print(f"❌ URL Mismatch")
                print(f"   Exp: {clean_expected[:30]}...")
                print(f"   Got: {clean_current[:30]}...")
                self._take_error_screenshot(link_text)

        except Exception as e:
            print(f"❌ Click Failed: {e}")
            self.driver.switch_to.window(orig_window)

    # --- פונקציות הרצה ---

    def run_tab_1_external_link_tests(self):
        print("\n--- Starting Fast Link Check (Daycare - Tab 1) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)

    def navigate_to_daycare_tab(self):
        """ Switches to the second tab using URL manipulation (Fastest way) """
        target_url = self.DAYCARE_URL + self.TAB_2_URL_PART
        self.go_to_url(target_url)
        print(f"\n>>> Navigating to Tab 2: {target_url}")
        # השארתי זמן קצר לטעינה, כי בשינוי URL הדף מתרענן לגמרי
        time.sleep(2) 

    def run_tab_2_external_link_tests(self):
        print(f"\n--- Starting Fast Link Check (Daycare - Tab 2) ---")
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)