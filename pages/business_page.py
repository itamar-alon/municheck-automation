import time
from selenium.webdriver.common.by import By
from .base_page import BasePage

class BusinessLicensePage(BasePage):
    """Business License Page Object - High Precision Link Validation with Visual Debugging."""

    # --- Locators ---
    PAGE_TITLE = (By.TAG_NAME, "h1")
    TAB_BUTTON_NAME_2 = "דרישות ותנאים, מפרטים והיתרים"
    TAB_BUTTON_NAME_3 = "טפסים"
    TAB_2_URL_PART = "tab=1"
    TAB_3_URL_PART = "tab=2"

    # --- Test Links Data ---
    TAB_1_EXTERNAL_LINKS = {
        "שלבים בפתיחת עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/NewBusiness.aspx",
        "הגשת בקשה מקוונת לרישיון עסק": "por141.cityforms.co.il/ApplicationBuilder/eFormRender.html",
    }
    
    TAB_2_EXTERNAL_LINKS = {
        "רישיון לניהול עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/License.aspx",
        "דרישות ותנאים לקבלת רישיון עסק": "default.aspx",
        "אתר המפרטים האחידים": "gov.il/he/departments/units/reform1/govil-landing-page",
        "בדיקת סטטוס רישוי": "https://city4u.co.il/PortalServicesSite/_portal/283000", 
        "דרישות לנגישות עסקים": "Accessibility.aspx",
    }
    
    TAB_3_EXTERNAL_LINKS = {
        "ושולחנות ומתקני": "TableAndChairsPermit141",
        "שולחנות וכיסאות": "cityPay/283000/mislaka/48",
        "בקשה לרישיון": "BusinessLicense141",
        "בדיקת סטטוס רישוי": "city4u.co.il/PortalServicesSite/_portal/283000",
        "אגרת רישוי עסק": "mislaka/118"
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.BUSINESS_URL = url

    def open_business_page(self):
        self.go_to_url(self.BUSINESS_URL)
        print(f">>> Navigated to: {self.BUSINESS_URL}")

    def get_page_title(self):
        return self.get_element(self.PAGE_TITLE).text

    def _verify_link_robust(self, link_text, expected_url_part):
        """ אימות הקישור: בדיקת סטטוס, ואם נכשל - פתיחה לטובת צילום מסך. """
        xpath = f"//a[contains(normalize-space(.), '{link_text}')]"
        try:
            link_element = self.get_element((By.XPATH, xpath))
            actual_url = link_element.get_attribute("href")
            
            if not actual_url:
                print(f"❌ No href found for: {link_text}")
                return False
            
            # 1. בדיקת URL טקסטואלית
            if expected_url_part not in actual_url:
                print(f"❌ URL Mismatch: {link_text}")
                self._open_and_switch_to_link(actual_url)
                return False

            # 2. בדיקת סטטוס שרת (מהירה)
            is_live, status = self.validate_link_status(actual_url)
            if is_live:
                print(f"✅ Live (200): {link_text}")
                return True
            else:
                print(f"❌ Broken ({status}): {link_text}. Opening for screenshot...")
                self._open_and_switch_to_link(actual_url)
                return False

        except Exception as e:
            print(f"❌ Not Found in DOM: {link_text} ({e})")
            return False

    def _open_and_switch_to_link(self, url):
        """ עזר: פתיחת טאב חדש ומעבר אליו כדי שהצילום מסך יתעד את השגיאה. """
        self.driver.execute_script("window.open(arguments[0], '_blank');", url)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(3) # זמן טעינה לדף השגיאה

    # --- Tab Functions ---

    def run_tab_1_external_link_tests(self):
        print("\n--- Testing Tab 1 Links ---")
        results = [self._verify_link_robust(name, url) for name, url in self.TAB_1_EXTERNAL_LINKS.items()]
        return all(results)

    def navigate_to_tab_2(self):
        print(f"\n--- Navigating to: {self.TAB_BUTTON_NAME_2} ---")
        locator = (By.XPATH, f"//button[contains(text(), '{self.TAB_BUTTON_NAME_2}')]")
        self.wait_for_clickable_element(locator).click()
        self.wait_for_url_to_contain(self.TAB_2_URL_PART)

    def run_tab_2_external_link_tests(self):
        print("--- Testing Tab 2 Links ---")
        results = [self._verify_link_robust(name, url) for name, url in self.TAB_2_EXTERNAL_LINKS.items()]
        return all(results)

    def navigate_to_tab_3(self):
        print(f"\n--- Navigating to: {self.TAB_BUTTON_NAME_3} ---")
        locator = (By.XPATH, f"//button[contains(text(), '{self.TAB_BUTTON_NAME_3}')]")
        self.wait_for_clickable_element(locator).click()
        self.wait_for_url_to_contain(self.TAB_3_URL_PART)

    def run_tab_3_external_link_tests(self):
        print("--- Testing Tab 3 Links ---")
        results = [self._verify_link_robust(name, url) for name, url in self.TAB_3_EXTERNAL_LINKS.items()]
        return all(results)