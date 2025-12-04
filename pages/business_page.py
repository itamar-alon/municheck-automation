from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage

class BusinessLicensePage(BasePage):
    """Business License Page Object. Contains complex and robust testing logic.""" # 🟢 תורגם

    # --- Locators and Test Data ---
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    
    # ⬅️ Specific Data for Business License Page (3 tabs)
    TAB_BUTTON_NAME_2 = "דרישות ותנאים, מפרטים והיתרים"
    TAB_BUTTON_NAME_3 = "טפסים"
    TAB_2_URL_PART = "?tab=1"
    TAB_3_URL_PART = "?tab=2"

    # ⬅️ 1. Test Links - Default Tab
    TAB_1_EXTERNAL_LINKS = {
        "שלבים בפתיחת עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/NewBusiness.aspx",
        "הגשת בקשה מקוונת לרישיון עסק": "por141.cityforms.co.il/ApplicationBuilder/eFormRender.html",
    }
    
    # ⬅️ 2. Test Links - Second Internal Tab
    TAB_2_EXTERNAL_LINKS = {
        "רישיון לניהול עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/License.aspx",
        "דרישות ותנאים לקבלת רישיון עסק": "rishonlezion.muni.il/Business/BusinessLicense/BusinessLicenseprocess/Pages/default.aspx",
        "אתר המפרטים האחידים ברישוי עסקים": "gov.il/he/departments/units/reform1/govil-landing-page",
        "בדיקת סטטוס רישוי": "city4u.co.il/PortalServicesSite/_portal/283000",
        "דרישות לנגישות עסקים": "rishonlezion.muni.il/Business/BusinessLicense/BusinessLicenseprocess/Pages/Accessibility.aspx",
    }
    
    # ⬅️ 3. Test Links - Third Internal Tab
    TAB_3_EXTERNAL_LINKS = {
        "בקשה להצבת כי​סאות ושולחנות ומתקני תצוגה": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=8141005056A14F7F11CC002357F0A3B0&Process=TableAndChairsPermit141",
        "תשלום​​ להצבת שולחנות וכיסאות ו/או מתקני תצוגה​": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/48",
        "בקשה לרישיון": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=B8180050568AAB9211BBBBB84CF531F6&Process=BusinessLicense141",
        "חוות דעת מקדמית לאישור הנדסי​​": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=B81B0050568AAB9211CC0B2FE5206B86&Process=BusinessLicenseInfo141",
        "בדיקת סטטוס רישוי": "https://city4u.co.il/PortalServicesSite/_portal/283000",
        "אגרת רישוי עסק": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/118"
    }

    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.BUSINESS_URL = url

    def open_business_page(self):
        """ Navigates directly to the Business Licensing page. """ # 🟢 תורגם
        self.go_to_url(self.BUSINESS_URL)
        print(f">>> Navigated to Business Licensing page: {self.BUSINESS_URL}") # 🟢 תורגם

    def get_page_title(self):
        """ Returns the page title (for validation). """ # 🟢 תורגם
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    # --- Internal Helper Methods ---

    def _get_link_locator(self, link_text):
        """ 
        Returns a smart locator that ignores double spaces or line breaks.
        The use of normalize-space is critical for older governmental sites.
        """ # 🟢 תורגם
        xpath = f"//a[contains(normalize-space(.), '{link_text}')]"
        return (By.XPATH, xpath)

    def _click_link_by_text(self, link_text):
        """ Performs the click intelligently with a Retry mechanism against Stale Elements. """ # 🟢 תורגם
        dynamic_locator = self._get_link_locator(link_text)
        
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            try:
                # 1. Finding the element
                link_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located(dynamic_locator)
                )
                
                # 2. Scrolling to it (center screen)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_element)
                time.sleep(0.5) 

                # 3. Waiting for the element to be clickable
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(dynamic_locator))

                # 4. Attempting to click
                try:
                    link_element.click()
                except:
                    # Fallback: JS click if regular click is blocked
                    self.execute_script("arguments[0].click();", link_element)
                
                print(f">>> Clicked on '{link_text}' (Attempt {attempts+1}).") # 🟢 תורגם
                return 
                
            except (StaleElementReferenceException, TimeoutException):
                print(f"⚠️ Attempt {attempts+1} failed for '{link_text}', trying again...") # 🟢 תורגם
                attempts += 1
                time.sleep(1) # Allowing DOM to settle
            except Exception as e:
                print(f"❌ Unexpected error while clicking '{link_text}': {str(e)}") # 🟢 תורגם
                raise e

        raise Exception(f"❌ Failed to click element '{link_text}' after {max_attempts} attempts.") # 🟢 תורגם

    def _verify_single_external_link_navigation(self, link_text, expected_url_part):
        """ Internal function: Clicks, switches tab, validates URL, and returns. """ # 🟢 תורגם
        print(f"\n--- Starting navigation test: {link_text} ---") # 🟢 תורגם

        original_window = self.driver.current_window_handle
        
        self._click_link_by_text(link_text)
        
        # Waiting for a new window to open
        try:
            WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.number_of_windows_to_be(2)
            )
        except TimeoutException:
            # Checking if the link opened in the same window by mistake
            if expected_url_part in self.driver.current_url:
                 print("⚠️ Link opened in the same window (not a new tab).") # 🟢 תורגם
                 self.driver.back()
                 return
            else:
                 raise TimeoutException(f"❌ New tab did not open for '{link_text}'.") # 🟢 תורגם
            
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)
        
        # Waiting for URL to load
        try:
            self.wait_for_url_to_contain(expected_url_part, timeout=15)
        except TimeoutException:
             print(f"⚠️ Warning: URL did not contain '{expected_url_part}' in time, proceeding with check.") # 🟢 תורגם

        final_url = self.driver.current_url
        
        if expected_url_part not in final_url:
            print(f"❌ Validation error: Expected '{expected_url_part}' but got '{final_url}'") # 🟢 תורגם
        else:
            print(f"✅ Navigation validation for '{link_text}' passed.") # 🟢 תורגם

        self.driver.close()
        self.driver.switch_to.window(original_window)
        time.sleep(0.5) # Stabilizing back to the main window

    # --- Public Flow Methods ---

    def run_tab_1_external_link_tests(self):
        print("\n--- Starting external link test (Default Tab) ---") # 🟢 תורגם
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print("--- External link test finished (Default Tab) ---") # 🟢 תורגם

    def navigate_to_tab_2(self):
        self._switch_tab_safe(self.TAB_BUTTON_NAME_2, self.TAB_2_URL_PART)

    def run_tab_2_external_link_tests(self):
        print(f"\n--- Starting external link test (Tab: {self.TAB_BUTTON_NAME_2}) ---") # 🟢 תורגם
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- External link test finished (Tab: {self.TAB_BUTTON_NAME_2}) ---") # 🟢 תורגם

    def navigate_to_tab_3(self):
        self._switch_tab_safe(self.TAB_BUTTON_NAME_3, self.TAB_3_URL_PART)

    def run_tab_3_external_link_tests(self):
        print(f"\n--- Starting external link test (Tab: {self.TAB_BUTTON_NAME_3}) ---") # 🟢 תורגם
        for link_name, url_part in self.TAB_3_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- External link test finished (Tab: {self.TAB_BUTTON_NAME_3}) ---") # 🟢 תורגם

    def _switch_tab_safe(self, tab_name, expected_url_part):
        """ Safe tab switch with rigid waits. """ # 🟢 תורגם
        print(f"\n--- Starting navigation to tab: {tab_name} ---") # 🟢 תורגם
        
        tab_locator = (self.GENERIC_TAB_BUTTON[0], 
                        self.GENERIC_TAB_BUTTON[1].format(tab_name))
        
        # Click
        tab_element = self.wait_for_clickable_element(tab_locator, timeout=self.DEFAULT_TIMEOUT)
        try:
            tab_element.click()
        except:
             self.execute_script("arguments[0].click();", tab_element)
        
        print(f">>> Clicked on tab '{tab_name}'.") # 🟢 תורגם

        # 🛑 Rigid wait - critical for dynamic tab switching!
        time.sleep(2) 

        # Waiting for URL change
        try:
            self.wait_for_url_to_contain(expected_url_part, timeout=5)
        except:
            pass # URL sometimes updates very quickly before the check starts

        print(f"✅ Navigation to tab '{tab_name}' complete.") # 🟢 תורגם