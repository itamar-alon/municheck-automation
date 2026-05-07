import logging
import os
import time
from datetime import datetime
from urllib.parse import unquote
from playwright.sync_api import Page, expect
from .base_page import BasePage

logger = logging.getLogger("SystemFlowLogger")

class ParkingPage(BasePage):
    """
    Parking Page Object.
    Optimized for FAST link checking + Error Screenshots using Playwright.
    Skips Login and Personal Info Tab as requested.
    """

    PAGE_TITLE = "h1"
    
    TAB_3_LOCATOR = "//button[normalize-space()='תווי חניה']"
    
    GENERIC_LINK_XPATH = "//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{}')]"


    TAB_1_EXTERNAL_LINKS = {
        "תשלום דו": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/4",
        "הודעת תשלום קנס": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/16",
        "התראה לפני עיקול": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/3",
        "צו עיקול מטלטלין": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/98",
        "שובר דחיית ערעור": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/36"
    }

    TAB_3_EXTERNAL_LINKS = {
        "רשימת אזורי חניה": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/LocalParkingTicketArea.aspx?prm=920082-1&language=he",
        "פירוט חניונים": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/Cityparking.aspx?prm=920082-1&language=he",
        "חידוש תו חניה": "https://mileon-portal.co.il/DynamicForm/resNew.aspx?prm=920082-1&language=he",
        "בדיקת תוקף": "https://mileon-portal.co.il/DynamicForm/ValidationLabelsNew.aspx?prm=920082-1&language=he",
        "השלמת מסמכים": "https://mileon-portal.co.il/DynamicForm/CompletingDocuments.aspx?prm=920082-1&language=he",
        "הקצאת חניה שמורה": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/DisabledParking.aspx"
    }

    def __init__(self, page: Page, url: str):
        super().__init__(page)
        self.DEFAULT_TIMEOUT = 10000  # 10 seconds in ms
        self.PARKING_URL = url

    def open_parking_page(self):
        self.go_to_url(self.PARKING_URL)
        logger.info(f">>> Navigated to Parking page: {self.PARKING_URL}")

    def get_page_title(self):
        return self.get_element(self.PAGE_TITLE).inner_text()

    def _take_error_screenshot(self, link_name):
        try:
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/error_parking_{safe_name}_{timestamp}.png"
            
            self.page.screenshot(path=filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save screenshot: {e}")

    def _verify_external_link(self, link_text, expected_url_part):
        logger.info(f"Testing: {link_text}")
        
        locator_str = self.GENERIC_LINK_XPATH.format(link_text)
        
        try:
            locator = self.get_element(locator_str, timeout=self.DEFAULT_TIMEOUT)
        except Exception:
            logger.error(f"❌ Link error: '{link_text}' (Element not found)")
            self._take_error_screenshot(link_text)
            return

        href = locator.get_attribute("href")

        try:
            if href and "http" in href:
                decoded_href = unquote(href)
                decoded_expected = unquote(expected_url_part)
                
                if decoded_expected in decoded_href:
                    logger.info(f"✅ Passed (HREF check): {link_text}")
                    return 

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
        logger.info("\n--- Starting Fast Link Check (Tab 1 - Fines) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)

    def navigate_to_tab_3(self):
        logger.info("\n--- Navigating to Tab 3: תווי חניה ---")
        try:
            tab = self.get_element(self.TAB_3_LOCATOR, timeout=self.DEFAULT_TIMEOUT)
            tab.scroll_into_view_if_needed()
            tab.click()
            logger.info(">>> Switched to Tab 3.")
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            logger.error(f"❌ Failed to switch to Tab 3: {e}")
            self._take_error_screenshot("tab_switch_fail")

    def run_tab_3_external_link_tests(self):
        logger.info("\n--- Starting Fast Link Check (Tab 3 - Parking Permits) ---")
        for link_name, url_part in self.TAB_3_EXTERNAL_LINKS.items():
            self._verify_external_link(link_name, url_part)
