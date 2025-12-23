from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage

class WaterPage(BasePage):
    """
    Water Interface Page Object. 
    Optimized with Fast Link Validation (href check) and English logging.
    """

    # --- Locators and Test Data ---
    GENERIC_LINK_BY_TEXT = (By.XPATH, "//a[contains(normalize-space(.), '{}')]")
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    # Tab Names (Hebrew remains as it appears on buttons)
    TAB_BUTTON_NAME_2 = "טפסים מקוונים" 
    TAB_BUTTON_NAME_3 = "טפסים להורדה"
    
    TAB_2_URL_PART = "?tab=1" 
    TAB_3_URL_PART = "?tab=2"

    # --- 1. Test Links - Default Tab (Water Accounts) ---
    TAB_1_EXTERNAL_LINKS = {
        "תשלום חשבון מים": "mast.co.il/15657/payment"
    }
    
    # --- 2. Test Links - Tab 2 (Online Forms) ---
    TAB_2_EXTERNAL_LINKS = {
        "עדכון מספר נפשות": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_nefashot.aspx",
        "צריכת מים משותפת": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_8_zriha_meshutefet.aspx",
        "הפקדת מפתח": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_6_key.aspx",
        "בקשה לפינוי ביוב": "meniv-rishon.co.il/Service/forms/Pages/form_3_pinui_biuv.aspx",
        "בירור חיוב בעד צריכת מים": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_8_zriha_meshutefet.aspx",
        "הכרה בתעריף מיוחד": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_5_mad_meshuyah.aspx",
        "מנזילה במערכת המים": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_4_nezila.aspx",
        "מסירת קריאת מונה": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_2_naul.aspx",
        "ביצוע בדיקות": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_9_bakasha_eihut_maim.aspx"
    }

    # --- 3. Test Links - Tab 3 (Downloadable Forms) ---
    TAB_3_EXTERNAL_LINKS = {
        "בקשה לביקור מתואם": "setvisit.pdf",
        "לקבלת מידע": "D7%91%D7%A7%D7%A9%D7%94%20%D7%9C%D7%A7%D7%91%D7%9C%D7%AA%20%D7%9E%D7%99%D7%93%D7%A2.pdf",
        "הוראה לחיוב בבנק": "D7%94%D7%95%D7%A8%D7%90%D7%94%20%D7%9C%D7%97%D7%99%D7%95%D7%91",
        "החלפת מחזיקים": "D7%94%D7%A6%D7%94%D7%A8%D7%94%20%D7%A2%D7%9C%20%D7%94%D7%97%D7%9C%D7%A4%D7%AA",
        "הנחיות להגשת תכנית": "D7%94%D7%A0%D7%97%D7%99%D7%95%D7%AA%20%D7%9C%D7%94%D7%92%D7%A9%D7%AA",
        "לקבלת תעודת גמר": "D7%98%D7%95%D7%A4%D7%A1%205%20%D7%9E%D7%A2%D7%95%D7%93%D7%9B%D7%9F",
        "עם כשרות מהודרת": "https://www.meniv-rishon.co.il/Service/forms/Documents/%D7%98%D7%95%D7%A4%D7%A1%20%D7%A0%D7%AA%D7%95%D7%A0%D7%99%D7%9D%20%D7%9E%D7%93%D7%99%20%D7%A7%D7%A8%D7%9E.pdf" 
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.WATER_URL = url
        self.TAB_1_NAME = "Water Accounts" 

    def open_water_page(self):
        """ Navigates directly to the Water Interface page. """
        self.go_to_url(self.WATER_URL)
        print(f">>> Navigated to Water Interface page: {self.WATER_URL}")

    def get_page_title(self):
        """ Returns the page title (for validation). """
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    # --- Internal Helper Methods (Fast Validation) ---
    
    def _verify_link_href_fast(self, link_text, expected_url_part):
        """ Checks the href attribute of a link without clicking it. """
        print(f"--- Checking link: {link_text} ---")
        xpath = f"//a[contains(normalize-space(.), '{link_text}')]"
        dynamic_locator = (By.XPATH, xpath)
        
        try:
            link_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(dynamic_locator)
            )
            actual_url = link_element.get_attribute("href")
            
            if not actual_url:
                print(f"❌ Error: Link '{link_text}' has no href attribute!")
                return False

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
        print(f"\n--- Starting Fast Link Check (Tab: {self.TAB_1_NAME}) ---")
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
        """ Safe tab switching with stability wait. """
        print(f"\n--- Navigating to tab: {tab_name} ---")
        tab_locator = (By.XPATH, f"//button[contains(text(), '{tab_name}')]")
        
        try:
            tab_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.element_to_be_clickable(tab_locator)
            )
            self.driver.execute_script("arguments[0].click();", tab_element)
            time.sleep(2) # Stabilize dynamic DOM
            print(f"✅ Successfully switched to tab '{tab_name}'.")
        except Exception as e:
            print(f"❌ Failed to switch to tab '{tab_name}': {e}")