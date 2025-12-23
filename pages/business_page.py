from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage

class BusinessLicensePage(BasePage):
    """Business License Page Object - Optimized for fast link validation."""

    # --- Locators and Test Data ---
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    
    TAB_BUTTON_NAME_2 = "דרישות ותנאים, מפרטים והיתרים"
    TAB_BUTTON_NAME_3 = "טפסים"
    TAB_2_URL_PART = "?tab=1"
    TAB_3_URL_PART = "?tab=2"

    # Test Links Data
    TAB_1_EXTERNAL_LINKS = {
        "שלבים בפתיחת עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/NewBusiness.aspx",
        "הגשת בקשה מקוונת לרישיון עסק": "por141.cityforms.co.il/ApplicationBuilder/eFormRender.html",
    }
    
    TAB_2_EXTERNAL_LINKS = {
        "רישיון לניהול עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/License.aspx",
        "דרישות ותנאים לקבלת רישיון עסק": "rishonlezion.muni.il/Business/BusinessLicense/BusinessLicenseprocess/Pages/default.aspx",
        "אתר המפרטים האחידים ברישוי עסקים": "gov.il/he/departments/units/reform1/govil-landing-page",
        "בדיקת סטטוס רישוי": "city4u.co.il/PortalServicesSite/_portal/283000",
        "דרישות לנגישות עסקים": "rishonlezion.muni.il/Business/BusinessLicense/BusinessLicenseprocess/Pages/Accessibility.aspx",
    }
    
    TAB_3_EXTERNAL_LINKS = {
        "ושולחנות ומתקני": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=8141005056A14F7F11CC002357F0A3B0&Process=TableAndChairsPermit141",
        "שולחנות וכיסאות": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/48",
        "בקשה לרישיון": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=B8180050568AAB9211BBBBB84CF531F6&Process=BusinessLicense141",
        "חוות דעת מקדמית לאישור הנדסי": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=B81B0050568AAB9211CC0B2FE5206B86&Process=BusinessLicenseInfo141",
        "בדיקת סטטוס רישוי": "https://city4u.co.il/PortalServicesSite/_portal/283000",
        "אגרת רישוי עסק": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/118"
    }

    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.BUSINESS_URL = url

    def open_business_page(self):
        """ניווט ישיר לעמוד רישוי עסקים."""
        self.go_to_url(self.BUSINESS_URL)
        print(f">>> Navigated to: {self.BUSINESS_URL}")

    def get_page_title(self):
        """החזרת כותרת העמוד לאימות."""
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    # --- Internal Helper Methods ---

    def _get_link_locator(self, link_text):
        """מציאת אלמנט קישור לפי הטקסט שלו בצורה גמישה."""
        xpath = f"//a[contains(normalize-space(.), '{link_text}')]"
        return (By.XPATH, xpath)

    def _verify_link_href_fast(self, link_text, expected_url_part):
        """
        השיטה המהירה: בודקת את ה-URL בקישור מבלי להקליק עליו.
        מונע טעינת עמודים חיצוניים ופופ-אפים.
        """
        print(f"--- Checking link: {link_text} ---")
        dynamic_locator = self._get_link_locator(link_text)
        
        try:
            # המתנה שהאלמנט יהיה קיים ב-DOM
            link_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(dynamic_locator)
            )
            
            # שליפת ה-URL מה-attribute 'href'
            actual_url = link_element.get_attribute("href")
            
            if not actual_url:
                print(f"❌ Error: Link '{link_text}' has no href attribute!")
                return False

            # בדיקה האם החלק המצופה נמצא בתוך ה-URL
            if expected_url_part in actual_url:
                print(f"✅ Fast Check Passed: '{link_text}' points to correct URL.")
                return True
            else:
                print(f"❌ Validation Failed: Expected '{expected_url_part}' but found '{actual_url}'")
                return False

        except (TimeoutException, StaleElementReferenceException):
            print(f"❌ Could not find link: '{link_text}'")
            return False

    # --- Public Flow Methods ---

    def run_tab_1_external_link_tests(self):
        print("\n--- Starting Fast Link Check (Default Tab) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_link_href_fast(link_name, url_part)

    def navigate_to_tab_2(self):
        self._switch_tab_safe(self.TAB_BUTTON_NAME_2, self.TAB_2_URL_PART)

    def run_tab_2_external_link_tests(self):
        print(f"\n--- Starting Fast Link Check (Tab: {self.TAB_BUTTON_NAME_2}) ---")
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_link_href_fast(link_name, url_part)

    def navigate_to_tab_3(self):
        self._switch_tab_safe(self.TAB_BUTTON_NAME_3, self.TAB_3_URL_PART)

    def run_tab_3_external_link_tests(self):
        print(f"\n--- Starting Fast Link Check (Tab: {self.TAB_BUTTON_NAME_3}) ---")
        for link_name, url_part in self.TAB_3_EXTERNAL_LINKS.items():
            self._verify_link_href_fast(link_name, url_part)

    def _switch_tab_safe(self, tab_name, expected_url_part):
        """מעבר בטוח בין טאבים פנימיים בעמוד."""
        print(f"\n--- Navigating to tab: {tab_name} ---")
        tab_locator = (By.XPATH, f"//button[contains(text(), '{tab_name}')]")
        
        try:
            tab_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.element_to_be_clickable(tab_locator)
            )
            self.driver.execute_script("arguments[0].click();", tab_element)
            
            # המתנה קצרה לעדכון ה-URL של הטאב
            time.sleep(1.5) 
            print(f"✅ Switched to tab '{tab_name}'.")
        except Exception as e:
            print(f"❌ Failed to switch to tab '{tab_name}': {e}")