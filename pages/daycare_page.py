from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from .base_page import BasePage 
from selenium.webdriver.common.by import By

class DaycarePage(BasePage):
    """Daycare/Kindergarten page class, containing robust testing logic."""

    # --- Locators and Test Data ---
    # Complex generic Locators for finding an <a> tag containing text as a descendant
    GENERIC_LINK_BY_TEXT = (By.XPATH, "//a[.//text()[contains(.,'{}')]]")
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    
    # 🛑 Reliable solution: Locator via CSS Selector using the URL (href)
    # This completely bypasses quoting/syntax issues in XPath.
    TAMAT_URL_PART = "CategoryID=3506"
    TAMAT_BUTTON_LOCATOR = (By.CSS_SELECTOR, f"a[href*='{TAMAT_URL_PART}']") 
    
    TAB_BUTTON_NAME = "מעונות יום" 
    TAB_2_URL_PART = "?tab=1" 

    # ⬅️ 1. Test Links - 'Daycare Centers' Tab (Default)
    TAB_1_EXTERNAL_LINKS = {
        "איזור אישי": "h5z.info-cloud.co.il",
        "רישום לצהרוני בית הספר": "h5z.info-cloud.co.il",
    }
    
    # ⬅️ 2. Test Links - 'Daycare Centers' Tab (New links)
    TAB_2_EXTERNAL_LINKS = {
        "אזור אישי": "h5z.info-cloud.co.il/Login?loginFor=PrivateArea", 
        "רישום מעונות יום": "h5z.info-cloud.co.il/Home/AnotherProcIsRunning?lang=he",
        # Link name in the dictionary remains as it appears in the check, for comparison only
        "רישום מעון חרצית תמ''ת": "https://www.hironit.org.il/?CategoryID=3506"
    }

    # Removed: TAMAT_BUTTON_NAME and TAMAT_BUTTON_XPATH
    
    PAGE_TITLE = (By.TAG_NAME, "h1")
    # ... (other relevant Locators) ...
    
    
    def __init__(self, driver, url):
        super().__init__(driver)
        self.DAYCARE_URL = url 

    def open_daycare_page(self):
        """ Navigates directly to the Daycare page. """
        self.go_to_url(self.DAYCARE_URL)
        print(f">>> Navigated to Daycare page: {self.DAYCARE_URL}") # 🟢 Translated

    def get_page_title(self):
        """ Returns the page title (for validation). """
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    
    # --- Internal Helper Methods ---
    
    def _click_link_by_text(self, link_text):
        """ Internal method: Performs the click on a specific link using JavaScript. """
        
        # 🛑 Critical change: If the link name is problematic, use CSS Selector (by URL)
        if link_text == "רישום מעון חרצית תמ''ת":
            dynamic_locator = self.TAMAT_BUTTON_LOCATOR
            print(f">>> Using HREF locator for '{link_text}'.") # 🟢 Translated
        else:
            # For all other links, use the generic XPath
            dynamic_locator = (self.GENERIC_LINK_BY_TEXT[0], 
                               self.GENERIC_LINK_BY_TEXT[1].format(link_text))
            
        # 1. Wait to ensure the element is clickable
        link_element = self.wait_for_clickable_element(dynamic_locator) 
        
        # 2. Execute direct JavaScript click
        self.execute_script("arguments[0].click();", link_element)
        print(f">>> Sent JavaScript click command for '{link_text}'.") # 🟢 Translated


    def _verify_single_external_link_navigation(self, link_text, expected_url_part):
        """ Internal function: Clicks, switches tab, validates URL, and returns (single check). """
        print(f"\n--- Starting navigation test: {link_text} ---") # 🟢 Translated

        original_window = self.driver.current_window_handle
        
        # 1. Performing the click that opens the new tab (uses the fixed method)
        self._click_link_by_text(link_text)
        
        # 2. Short wait for the new tab to open and switch to it
        new_window = None
        for _ in range(10): 
            if len(self.driver.window_handles) > 1:
                new_window = [window for window in self.driver.window_handles if window != original_window][0]
                self.driver.switch_to.window(new_window)
                print(">>> Switched to the new tab.") # 🟢 Translated
                break
            time.sleep(1)

        if not new_window:
            raise TimeoutException(f"❌ New tab did not open after clicking '{link_text}'.") # 🟢 Translated

        # 3. Validating the external URL
        self.wait_for_url_to_contain(expected_url_part, timeout=15)
        
        final_url = self.driver.current_url
        assert expected_url_part in final_url, f"❌ Navigation did not lead to the correct external address! Found: {final_url}" # 🟢 Translated
        
        print(f"✅ Navigation validation for '{link_text}' passed. Target URL: {final_url}") # 🟢 Translated

        # 4. Closing the new tab and returning to the original tab
        self.driver.close()
        self.driver.switch_to.window(original_window)
        print(">>> Returned to original tab. Test ready to continue.") # 🟢 Translated

    # --- Public Flow Methods (used by full_flow.py) ---

    def run_tab_1_external_link_tests(self):
        """ Runs a loop over all external links in the 'Daycare Centers' tab. """
        print("\n--- Starting external link test (Daycare Centers Tab) ---") # 🟢 Translated
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print("--- External link test finished (Daycare Centers Tab) ---") # 🟢 Translated


    def navigate_to_daycare_tab(self):
        """ 
        ⬅️ Alternative solution: Navigate directly to the tab URL to prevent crashes. 
        """
        target_url = self.DAYCARE_URL + self.TAB_2_URL_PART
        
        # 1. Direct navigation to the new URL (bypassing the problematic click)
        self.go_to_url(target_url) 
        print(f"\n>>> Bypassing problematic click. Navigated directly to tab URL: {target_url}") # 🟢 Translated

        # 2. Waiting for DOM stability (waiting for the first element in the new tab)
        first_link_name = list(self.TAB_2_EXTERNAL_LINKS.keys())[0] 
        dynamic_locator = (self.GENERIC_LINK_BY_TEXT[0], 
                           self.GENERIC_LINK_BY_TEXT[1].format(first_link_name))
        
        # Waiting until the first link in the new tab is clickable:
        self.wait_for_clickable_element(dynamic_locator)
        print(">>> Elements in the new tab are stable and ready for clicking.") # 🟢 Translated
        
        final_url = self.driver.current_url
        if self.TAB_2_URL_PART not in final_url:
             raise Exception(f"❌ Internal URL did not change as expected! Found: {final_url}") # 🟢 Translated
             
        print(f"✅ Internal navigation to tab '{self.TAB_BUTTON_NAME}' passed. URL: {final_url}") # 🟢 Translated


    def run_tab_2_external_link_tests(self):
        """ Runs a loop over all external links in the 'Daycare Centers' tab. """
        print(f"\n--- Starting external link test (Tab: {self.TAB_BUTTON_NAME}) ---") # 🟢 Translated
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- External link test finished (Tab: {self.TAB_BUTTON_NAME}) ---") # 🟢 Translated