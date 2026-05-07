import logging
import os
import time
from datetime import datetime
from urllib.parse import unquote
from playwright.sync_api import Page, expect
from .base_page import BasePage

logger = logging.getLogger("SystemFlowLogger")

class BusinessLicensePage(BasePage):
    """
    Business License Page Object.
    Optimized for FAST link checking + Error Screenshots using Playwright.
    """

    PAGE_TITLE = "h1"
    GENERIC_LINK_XPATH = "//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{}')]"
    
    TAB_BUTTON_NAME_2 = "דרישות ותנאים, מפרטים והיתרים"
    TAB_BUTTON_NAME_3 = "טפסים"
    
    TAB_2_LOCATOR = f"//button[contains(text(), '{TAB_BUTTON_NAME_2}')]"
    TAB_3_LOCATOR = f"//button[contains(text(), '{TAB_BUTTON_NAME_3}')]"
    
    TAB_2_URL_PART = "tab=1"
    TAB_3_URL_PART = "tab=2"

    TAB_1_LINKS = {
        "שלבים ב": "rishonlezion.muni.il/Business/BusinessLicense/Pages/NewBusiness.aspx",
        "הגשת בקשה": "por141.cityforms.co.il/ApplicationBuilder/eFormRender.html",
    }
    
    TAB_2_LINKS = {
        "רישיון לניהול עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/License.aspx",
        "דרישות ותנאים לקבלת רישיון עסק": "default.aspx",
        "אתר המפרטים האחידים": "gov.il/he/departments/units/reform1/govil-landing-page",
        "בדיקת סטטוס רישוי": "https://city4u.co.il/PortalServicesSite/_portal/283000", 
        "דרישות לנגישות עסקים": "Accessibility.aspx",
    }
    
    TAB_3_LINKS = {
        "ושולחנות ומתקני": "TableAndChairsPermit141",
        "שולחנות וכיסאות": "cityPay/283000/mislaka/48",
        "בקשה לרישיון": "BusinessLicense141",
        "בדיקת סטטוס רישוי": "city4u.co.il/PortalServicesSite/_portal/283000",
        "אגרת רישוי עסק": "mislaka/118"
    }

    def __init__(self, page: Page, url: str):
        super().__init__(page)
        self.DEFAULT_TIMEOUT = 10000  # 10 seconds in ms
        self.BUSINESS_URL = url

    def open_business_page(self):
        self.go_to_url(self.BUSINESS_URL)
        logger.info(f">>> Navigated to Business page: {self.BUSINESS_URL}")

    def get_page_title(self):
        return self.get_element(self.PAGE_TITLE).inner_text()

    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/error_business_{safe_name}_{timestamp}.png"
            self.page.screenshot(path=filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save screenshot: {e}")

    def _verify_external_link(self, link_text, expected_url_part):
        logger.info(f"Testing: {link_text}")
        
        locator_str = self.GENERIC_LINK_XPATH.format(link_text)
        
        try:
            # Check if element exists and is visible using BasePage method
            locator = self.get_element(locator_str, timeout=self.DEFAULT_TIMEOUT)
        except Exception:
            logger.error(f"❌ Link error: '{link_text}' (Element not found or not visible)")
            self._take_error_screenshot(link_name=link_text)
            return

        href = locator.get_attribute("href")

        try:
            # Fast check if HREF already matches
            if href and "http" in href:
                decoded_href = unquote(href)
                decoded_expected = unquote(expected_url_part)
                if decoded_expected in decoded_href:
                    logger.info(f"✅ Passed (HREF check): {link_text}")
                    return 

            # Otherwise, click and verify new page
            with self.page.expect_popup() as popup_info:
                locator.scroll_into_view_if_needed()
                locator.click()
            
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
            logger.error(f"❌ Link error: '{link_text}' (Failed to open/verify). Error: {e}")
            self._take_error_screenshot(link_text)

    def run_tab_1_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Business - Tab 1) ---")
        for link_name, url_part in self.TAB_1_LINKS.items():
            self._verify_external_link(link_name, url_part)

    def navigate_to_tab_2(self):
        logger.info(f"\n--- Navigating to Tab 2: {self.TAB_BUTTON_NAME_2} ---")
        try:
            tab = self.get_element(self.TAB_2_LOCATOR, timeout=self.DEFAULT_TIMEOUT)
            tab.scroll_into_view_if_needed()
            tab.click()
            logger.info(">>> Switched to Tab 2.")
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.error(f"❌ Failed to switch to Tab 2: {e}")
            self._take_error_screenshot("tab_2_switch_fail")

    def run_tab_2_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Business - Tab 2) ---")
        for link_name, url_part in self.TAB_2_LINKS.items():
            self._verify_external_link(link_name, url_part)

    def navigate_to_tab_3(self):
        logger.info(f"\n--- Navigating to Tab 3: {self.TAB_BUTTON_NAME_3} ---")
        try:
            tab = self.get_element(self.TAB_3_LOCATOR, timeout=self.DEFAULT_TIMEOUT)
            tab.scroll_into_view_if_needed()
            tab.click()
            logger.info(">>> Switched to Tab 3.")
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.error(f"❌ Failed to switch to Tab 3: {e}")
            self._take_error_screenshot("tab_3_switch_fail")

    def run_tab_3_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Business - Tab 3) ---")
        for link_name, url_part in self.TAB_3_LINKS.items():
            self._verify_external_link(link_name, url_part)
