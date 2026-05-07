import logging
import os
import time
from datetime import datetime
from urllib.parse import unquote
from playwright.sync_api import Page, expect
from .base_page import BasePage

logger = logging.getLogger("SystemFlowLogger")

class DaycarePage(BasePage):
    """
    Daycare page class.
    OPTIMIZED: Includes Fast HREF Checking (Smart Verify) using Playwright.
    """

    PAGE_TITLE = "h1"
    GENERIC_LINK_XPATH = "//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{}')]"

    TAB_BUTTON_NAME = "מעונות יום"
    TAB_2_URL_PART = "?tab=1" 

    TAB_1_EXTERNAL_LINKS = {
        "איזור אישי": "cewz20", 
        "רישום לצהרוני בית הספר": "cewz20",
    }
    
    TAB_2_EXTERNAL_LINKS = {
        "אזור אישי": "PrivateArea",
        "רישום מעונות יום": "AnotherProcIsRunning",
        "רישום מעון חרצית": "CategoryID=3506"
    }

    def __init__(self, page: Page, url: str):
        super().__init__(page)
        self.DEFAULT_TIMEOUT = 10000  # 10 seconds in ms
        self.DAYCARE_URL = url

    def open_daycare_page(self):
        self.go_to_url(self.DAYCARE_URL)
        logger.info(f">>> Navigated to Daycare page: {self.DAYCARE_URL}")

    def get_page_title(self):
        return self.get_element(self.PAGE_TITLE).inner_text()
    
    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            timestamp = datetime.now().strftime("%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/err_daycare_{safe_name}_{timestamp}.png"
            self.page.screenshot(path=filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save screenshot: {e}")

    def _verify_external_link(self, link_text, expected_url_part):
        logger.info(f"Testing: {link_text}...") 
        
        locator_str = self.GENERIC_LINK_XPATH.format(link_text)
        
        try:
            # Check if element exists and is visible using BasePage method
            locator = self.get_element(locator_str, timeout=self.DEFAULT_TIMEOUT)
        except Exception:
            logger.error(f"❌ Not Found: {link_text}")
            self._take_error_screenshot(link_text)
            return

        href = locator.get_attribute("href")
        
        clean_href = unquote(href).replace("https://", "").replace("http://", "") if href else ""
        clean_expected = unquote(expected_url_part).replace("https://", "").replace("http://", "")

        if clean_expected in clean_href:
            logger.info(f"✅ OK (HREF): {link_text}")
            return 

        logger.warning(f"⚠️ Mismatch for '{link_text}' ('{clean_expected}' not in '{clean_href[:20]}...'), clicking...")
        
        try:
            with self.page.expect_popup() as popup_info:
                # Some sites might need specific attributes or script-based clicks if they don't use standard hrefs
                locator.scroll_into_view_if_needed()
                locator.click()
            
            new_page = popup_info.value
            new_page.wait_for_load_state()
            
            current_url = unquote(new_page.url)
            clean_current = current_url.replace("https://", "").replace("http://", "")
            
            if clean_expected in clean_current:
                logger.info(f"✅ OK (Clicked): {link_text}")
            else:
                logger.error(f"❌ URL Mismatch for {link_text}")
                logger.error(f"   Exp: ...{clean_expected[-30:]}")
                logger.error(f"   Got: ...{clean_current[-30:]}")
                self._take_error_screenshot(link_text)
            
            new_page.close()

        except Exception as e:
            logger.error(f"❌ Click Failed for {link_text}: {e}")
            self._take_error_screenshot(link_name=link_text)

    def run_tab_1_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Daycare - Tab 1) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)

    def navigate_to_daycare_tab(self):
        """ Switches to the second tab using URL manipulation (Fastest way) """
        target_url = self.DAYCARE_URL + self.TAB_2_URL_PART
        self.go_to_url(target_url)
        logger.info(f"\n>>> Navigating to Tab 2: {target_url}")
        self.page.wait_for_load_state("networkidle")

    def run_tab_2_external_link_tests(self):
        logger.info(f"\n--- Starting Fast Link Check (Daycare - Tab 2) ---")
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)
