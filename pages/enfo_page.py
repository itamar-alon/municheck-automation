import logging
import os
import time
from datetime import datetime
from urllib.parse import unquote
from playwright.sync_api import Page, expect
from .base_page import BasePage

logger = logging.getLogger("SystemFlowLogger")

class EnforcementPage(BasePage):
    """
    Class representing the Municipal Enforcement page.
    Refactored for Playwright - Optimized with Fast Link Check & Error Screenshots.
    """

    PAGE_TITLE_SELECTOR = "h1"

    TAB_1_EXTERNAL_LINKS = {
        "תשלום דו": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/77",
        "הודעת תשלום קנס": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/78",
        "התראה לפני עיקול": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/79" ,
        "צו עיקול": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/203",
        "שובר דחיית": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/76",
        "צפייה בפרטי": "https://city4u.co.il/PortalServicesSite/requestsManagement/283000/GetDochDetails/2",
        "סטטוס ערעור": "https://city4u.co.il/PortalServicesSite/requestsManagement/283000/GetStatus/2",
        "בקשה לביטול": "https://por140.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=81140050568A4D0111CC9E33E032EFBD&Process=CitizenAppealPikuach140"
    }

    def __init__(self, page: Page, url: str):
        super().__init__(page)
        self.DEFAULT_TIMEOUT = 10000  # ms
        self.ENFORCEMENT_URL = url

    def open_enforcement_page(self):
        self.go_to_url(self.ENFORCEMENT_URL)
        logger.info(f">>> Navigated to Enforcement page: {self.ENFORCEMENT_URL}")

    def get_page_title(self):
        return self.get_element(self.PAGE_TITLE_SELECTOR).inner_text()
    
    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/error_enfo_{safe_name}_{timestamp}.png"
            
            self.page.screenshot(path=filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save screenshot: {e}")

    def _verify_external_link(self, link_text, expected_url_part):
        logger.info(f"Testing: {link_text}")
        
        # Playwright selector for the link
        selector = f"xpath=//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{link_text}')]"
        
        try:
            # Check if element is present/attached using BasePage method
            locator = self.get_element(selector, timeout=self.DEFAULT_TIMEOUT)
        except Exception:
            logger.error(f"❌ Link error: '{link_text}' (Element not found)")
            self._take_error_screenshot(link_name=link_text)
            return

        href = locator.get_attribute("href") or ""

        try:
            # 1. HREF Check (Fastest)
            if href and "http" in href:
                decoded_href = unquote(href)
                decoded_expected = unquote(expected_url_part)
                
                if decoded_expected in decoded_href:
                    logger.info(f"✅ Passed (HREF check): {link_text}")
                    return 

            # 2. Click & New Window Check
            with self.page.expect_popup() as popup_info:
                locator.scroll_into_view_if_needed()
                locator.click(force=True)
            
            new_page = popup_info.value
            new_page.wait_for_load_state()
            
            current_url = unquote(new_page.url)
            expected_decoded = unquote(expected_url_part)

            if expected_decoded in current_url:
                logger.info(f"✅ Passed: {link_text}")
            else:
                logger.warning(f"⚠️ Warning: {link_text} opened but URL differs.\n   Expected: ...{expected_decoded[-20:]}\n   Got:      ...{current_url[-20:]}")

            new_page.close()

        except Exception as e:
            logger.error(f"❌ Link error: '{link_text}' (Failed to verify). Error: {e}")
            self._take_error_screenshot(link_text)

    def run_tab_1_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Reports and Fines Tab) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)
        logger.info("--- Link check finished ---")
