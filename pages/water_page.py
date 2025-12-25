import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage

class WaterPage(BasePage):
    """Water Interface Page Object - Robust Link Validation with Visual Debugging."""

    # --- Locators ---
    PAGE_TITLE = (By.TAG_NAME, "h1")
    TAB_BUTTON_NAME_2 = "טפסים מקוונים" 
    TAB_BUTTON_NAME_3 = "טפסים להורדה"
    TAB_2_URL_PART = "tab=1" 
    TAB_3_URL_PART = "tab=2"

    # --- Test Links Data ---
    TAB_1_EXTERNAL_LINKS = {
        "תשלום חשבון מים": "mast.co.il/15657/payment"
    }
    
    TAB_2_EXTERNAL_LINKS = {
        "עדכון מספר נפשות": "form_nefashot.aspx",
        "צריכת מים משותפת": "form_8_zriha_meshutefet.aspx",
        "הפקדת מפתח": "form_6_key.aspx",
        "בקשה לפינוי ביוב": "form_3_pinui_biuv.aspx",
        "הכרה בתעריף מיוחד": "form_5_mad_meshuyah.aspx",
        "מנזילה במערכת המים": "form_4_nezila.aspx",
        "מסירת קריאת מונה": "form_2_naul.aspx",
        "ביצוע בדיקות": "form_9_bakasha_eihut_maim.aspx"
    }

    TAB_3_EXTERNAL_LINKS = {
        "בקשה לביקור מתואם": "setvisit.pdf",
        "לקבלת מידע": "D7%91%D7%A7%D7%A9%D7%94%20%D7%9C%D7%A7%D7%91%D7%9C%D7%AA%20%D7%9E%D7%99%D7%93%D7%A2.pdf",
        "הוראה לחיוב בבנק": "D7%94%D7%95%D7%A8%D7%90%D7%94%20%D7%9C%D7%97%D7%99%D7%95%D7%91",
        "החלפת מחזיקים": "D7%94%D7%A6%D7%94%D7%A8%D7%94%20%D7%A2%D7%9C%20%D7%94%D7%97%D7%9C%D7%A4%D7%AA",
        "עם כשרות מהודרת": "Documents/%D7%98%D7%95%D7%A4%D7%A1%20%D7%A0%D7%AA%D7%95%D7%A0%D7%99%D7%9D%20%D7%9E%D7%93%D7%99%20%D7%A7%D7%A8%D7%9E.pdf" 
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.WATER_URL = url

    def open_water_page(self):
        self.go_to_url(self.WATER_URL)
        print(f">>> Navigated to: {self.WATER_URL}")

    def get_page_title(self):
        return self.get_element(self.PAGE_TITLE).text

    def _verify_link_robust(self, link_text, expected_url_part):
        """ אימות הקישור: בדיקת URL וסטטוס. אם נכשל - פותח טאב חדש לצילום מסך. """
        xpath = f"//a[contains(normalize-space(.), '{link_text}')]"
        try:
            link_element = self.get_element((By.XPATH, xpath))
            actual_url = link_element.get_attribute("href")
            
            if not actual_url:
                print(f"❌ No href found for: {link_text}")
                return False
            
            # 1. בדיקת URL טקסטואלית
            if expected_url_part not in actual_url:
                print(f"❌ URL Mismatch: {link_text} (Found: {actual_url})")
                self._open_and_switch_to_link(actual_url)
                return False

            # 2. בדיקת סטטוס שרת
            is_live, status = self.validate_link_status(actual_url)
            if is_live:
                print(f"✅ Pass (200): {link_text}")
                return True
            else:
                print(f"❌ Broken ({status}): {link_text}. Opening UI for screenshot...")
                self._open_and_switch_to_link(actual_url)
                return False

        except Exception as e:
            print(f"❌ Not Found in DOM: {link_text}")
            return False

    def _open_and_switch_to_link(self, url):
        """ עוזר: פתיחת טאב חדש ומעבר אליו לטובת צילום המסך בטסט. """
        self.driver.execute_script("window.open(arguments[0], '_blank');", url)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(3)

    # --- Navigation & Tests ---

    def run_tab_1_tests(self):
        print("\n--- Testing Tab 1 (Accounts) ---")
        return all([self._verify_link_robust(n, u) for n, u in self.TAB_1_EXTERNAL_LINKS.items()])

    def navigate_to_tab_2(self):
        print(f"\n--- Navigating to: {self.TAB_BUTTON_NAME_2} ---")
        locator = (By.XPATH, f"//button[contains(text(), '{self.TAB_BUTTON_NAME_2}')]")
        self.wait_for_clickable_element(locator).click()
        self.wait_for_url_to_contain(self.TAB_2_URL_PART)

    def run_tab_2_tests(self):
        print("--- Testing Tab 2 (Online Forms) ---")
        return all([self._verify_link_robust(n, u) for n, u in self.TAB_2_EXTERNAL_LINKS.items()])

    def navigate_to_tab_3(self):
        print(f"\n--- Navigating to: {self.TAB_BUTTON_NAME_3} ---")
        locator = (By.XPATH, f"//button[contains(text(), '{self.TAB_BUTTON_NAME_3}')]")
        self.wait_for_clickable_element(locator).click()
        self.wait_for_url_to_contain(self.TAB_3_URL_PART)

    def run_tab_3_tests(self):
        print("--- Testing Tab 3 (Download Forms) ---")
        return all([self._verify_link_robust(n, u) for n, u in self.TAB_3_EXTERNAL_LINKS.items()])