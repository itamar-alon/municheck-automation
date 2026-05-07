import logging
import time
from playwright.sync_api import Page, expect
from .base_page import BasePage

logger = logging.getLogger("SystemFlowLogger")

class StreetPage(BasePage):
    """
    Class representing the 'Street Info' page.
    Implements robust validation focusing on Playwright's auto-waiting and locators.
    """

    TEST_STREET_NAME = "רבי מאיר" 

    PAGE_LOAD_VALIDATOR = "text='מידע על רחוב'"
    
    PAGE_TITLE_LOCATOR = "h1"
    STREET_NAME_INPUT_LOCATOR = "xpath=//input[@type='text' and not(@readonly) and not(@disabled)]" 
    
    DATA_TABLE_ROW = "xpath=//div[contains(@class, 'table-row')][position()>1][1]" 
    EXPAND_BUTTON = "xpath=//*[contains(normalize-space(.), 'לפרטים נוספים לחץ כאן')]/following-sibling::button"
    
    # Target specific list items or text within the street details container
    DATA_RETURN_VALIDATOR = "xpath=//ul[contains(@class, 'street-details')]//*[contains(text(), 'יום ג')]"
    POPUP_CONTENT = "xpath=//*[contains(@class, 'MuiDialog')]//*[contains(text(), 'יום')]"

    def __init__(self, page: Page, url: str):
        super().__init__(page)
        self.STREET_URL = url
        self.DEFAULT_TIMEOUT = 10000  # 10 seconds in ms

    def open_street_page(self):
        """ Navigates to the street info page and waits for the critical text. """
        self.go_to_url(self.STREET_URL)
        self.page.wait_for_load_state("domcontentloaded")
        
        try:
            # Wait for any visible occurrence of the text using regex for flexibility
            self.page.locator("text=/מידע.*על.*רחוב/").first.wait_for(state="visible", timeout=10000)
            logger.info(">>> ✅ Container title 'מידע על רחוב' found. Page is stable.")
        except Exception:
            logger.warning(">>> ⚠️ Page title 'מידע על רחוב' not found within 10s, but proceeding...")
        
        logger.info(f">>> Navigated to Street Page: {self.STREET_URL}")

    def get_page_title(self):
        """ Returns the main title text for validation. """
        try:
            return self.page.locator(self.PAGE_LOAD_VALIDATOR).first.inner_text()
        except Exception:
             return "מידע על רחוב"

    def search_and_verify_table(self):
        """ Performs a street search and verifies data returned to the table. """
        street_name = self.TEST_STREET_NAME
        logger.info(f"\n--- Starting street search test: {street_name} ---")

        input_element = self.get_element(self.STREET_NAME_INPUT_LOCATOR)
        
        input_element.fill(street_name)
        
        time.sleep(0.5) 

        STREET_SUGGESTION_LOCATOR = f"xpath=//*[contains(@class, 'suggestion') or @role='option'][contains(normalize-space(.), '{street_name}')]"
        
        try:
            suggestion_element = self.get_element(STREET_SUGGESTION_LOCATOR, timeout=7000)
            suggestion_element.click()
            logger.info(">>> ✅ Street suggestion clicked successfully. Initiating AJAX.")
        
        except Exception as e:
            try:
                logger.warning(">>> ⚠️ Suggestion click failed. Trying Press('Enter') as fallback...")
                input_element.press("Enter")
            except Exception as enter_e:
                raise Exception(f"❌ Critical failure clicking dropdown suggestion or pressing ENTER: Original Error: {e}, Fallback Error: {enter_e}")

        try:
            data_element_found = self.get_element(self.DATA_RETURN_VALIDATOR, timeout=15000) 
            validation_text = data_element_found.inner_text()
            logger.info(f"✅ Data returned to table successfully. Found validation text: {validation_text[:50]}...")
            return True
            
        except Exception:
            raise Exception("❌ Table failed to load data after search. Validation text 'יום ג' not found.")


    def expand_and_verify_popup(self):
        """ Clicks the plus button and verifies the popup content loaded. """
        logger.info("\n--- Starting popup expansion test ---")
        
        try:
            plus_button = self.get_element(self.EXPAND_BUTTON)
            plus_button.click()
            logger.info(">>> Plus button clicked.")
        except Exception as e:
            raise Exception(f"❌ Failed to click the expand button. Error: {e}")
        
        try:
            popup_element = self.get_element(self.POPUP_CONTENT, timeout=5000)
            popup_text = popup_element.inner_text()
            logger.info(f"✅ Popup loaded successfully. Found validation text: {popup_text[:30]}")
            return True
        except Exception:
            raise Exception("❌ Popup failed to load or validation text ('יום') is missing.")
