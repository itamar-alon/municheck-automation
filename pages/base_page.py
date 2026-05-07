import requests
import logging
from playwright.sync_api import Page, Locator, expect

logger = logging.getLogger("SystemFlowLogger")

class BasePage:
    """
    Base class for all Page Objects using Playwright.
    """
    
    DEFAULT_WAIT_TIME = 10000  # 10 seconds in milliseconds
    
    def __init__(self, page: Page):
        self.page = page

    def dismiss_cookie_banner(self):
        """
        Attempts to find and click common cookie consent buttons.
        """
        try:
            cookie_btn = self.page.locator("//button[contains(text(), 'מאשר') or contains(text(), 'אישור') or contains(text(), 'הבנתי')]")
            if cookie_btn.is_visible(timeout=3000):
                cookie_btn.click()
                logger.info("🍪 Cookie banner closed successfully.")
        except Exception:
            # We ignore failures here as cookie banners might not be present
            pass

    def validate_link_status(self, url):
        """
        Performs an HTTP request to check if a link is alive.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.head(url, allow_redirects=True, timeout=5, headers=headers)
            if response.status_code >= 400:
                response = requests.get(url, allow_redirects=True, timeout=5, stream=True, headers=headers)
            
            is_success = response.status_code == 200
            
            if not is_success:
                self._record_broken_link(url, response.status_code)
                
            return is_success, response.status_code
            
        except Exception as e:
            self._record_broken_link(url, str(e))
            return False, str(e)

    def _record_broken_link(self, url, reason):
        """
        Records a broken link in a list attached to the page object for reporting.
        """
        if not hasattr(self.page, 'broken_links_list'):
            self.page.broken_links_list = []
            
        entry = f"URL: {url} | Reason/Status: {reason}"
        if entry not in self.page.broken_links_list:
            self.page.broken_links_list.append(entry)
            logger.warning(f"⚠️ Broken link recorded: {entry}")

    def go_to_url(self, url):
        logger.info(f"Navigating to URL: {url}")
        self.page.goto(url)

    def execute_script(self, script, arg=None):
        return self.page.evaluate(script, arg)

    def get_element(self, selector, timeout=None):
        """
        Returns a locator for the given selector and waits for it to be visible.
        """
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout or self.DEFAULT_WAIT_TIME)
        return locator

    def wait_for_clickable_element(self, selector, timeout=None):
        """
        Waits for an element to be visible and returns the locator. 
        Playwright handles 'clickability' automatically during click().
        """
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout or self.DEFAULT_WAIT_TIME)
        return locator

    def wait_for_url_to_contain(self, url_part, timeout=None):
        import re
        self.page.wait_for_url(re.compile(f".*{re.escape(url_part)}.*"), timeout=timeout or self.DEFAULT_WAIT_TIME)
