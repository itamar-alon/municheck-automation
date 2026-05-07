from playwright.sync_api import Page, expect
from .base_page import BasePage
import time
import logging

logger = logging.getLogger("SystemFlowLogger")

class LoginPage(BasePage):
    """Class representing the Login page, supporting password login and login within a modal."""

    PASSWORD_TAB_TEXT = "באמצעות סיסמה"
    # Using text selector for the button
    PASSWORD_TAB_SELECTOR = f"button:has-text('{PASSWORD_TAB_TEXT}')"
    
    # Flexible ID field selector
    ID_FIELD_SELECTOR = "input[name='identityNumber'], input[name='tz'], input[type='text'], input[type='number']"
    PASSWORD_FIELD_SELECTOR = "input[name='password']"
    
    FINAL_LOGIN_BUTTON_TEXT = "כניסה"
    FINAL_LOGIN_BUTTON_SELECTOR = f"button:has-text('{FINAL_LOGIN_BUTTON_TEXT}')"
    
    OVERLAY_SELECTOR = ".MuiDialog-container[role='presentation']"

    def __init__(self, page: Page, url: str):
        super().__init__(page) 
        self.LOGIN_URL = url 

    def login_with_password(self, user_id: str, user_password: str):
        self.go_to_url(self.LOGIN_URL)
        logger.info(f">>> Navigated to: {self.LOGIN_URL}")
        
        # Click on password tab
        try:
            tab = self.page.locator(self.PASSWORD_TAB_SELECTOR).first
            tab.wait_for(state="visible", timeout=10000)
            tab.click(force=True)
            logger.info(f">>> Clicked on tab '{self.PASSWORD_TAB_TEXT}'.")
        except Exception as e:
            logger.warning(f">>> Failed to click on password tab: {e}")

        # Fill ID and Password
        id_field = self.page.locator(self.ID_FIELD_SELECTOR).first
        id_field.wait_for(state="visible", timeout=10000)
        id_field.fill(str(user_id))
        logger.info(">>> Entered ID number")

        password_field = self.page.locator(self.PASSWORD_FIELD_SELECTOR)
        password_field.fill(str(user_password))
        logger.info(">>> Entered password")

        # Handle Overlay / Submit
        try:
            overlay = self.page.locator(self.OVERLAY_SELECTOR)
            if overlay.is_visible():
                overlay.wait_for(state="hidden", timeout=5000)
        except Exception:
            logger.warning(">>> Overlay did not disappear, continuing with force click.")

        login_button = self.page.locator(self.FINAL_LOGIN_BUTTON_SELECTOR).first
        login_button.click(force=True)
        logger.info(f">>> Clicked on button '{self.FINAL_LOGIN_BUTTON_TEXT}'.")

    def wait_for_successful_login(self, home_url_part: str):
        self.wait_for_url_to_contain(home_url_part, timeout=20000)
        logger.info(f">>> Successful navigation to URL containing '{home_url_part}'.")

    def login_with_password_inside_modal(self, id_number: str, password: str, frame=None):
        user_id_str = str(id_number)
        user_password_str = str(password)
        
        # Use the provided frame or the default page object
        target = frame if frame else self.page

        try:
            # Using XPATH for strict matching if needed, but Playwright text selectors are usually better
            password_tab = target.locator("//button[normalize-space(text())='באמצעות סיסמה']").first
            if password_tab.is_visible(timeout=5000):
                password_tab.click()
                logger.info(">>> Clicked 'באמצעות סיסמה' tab inside modal")
                self.page.wait_for_timeout(1000)
        except Exception:
            logger.info(">>> 'באמצעות סיסמה' tab not found or already active, continuing...")

        id_input = target.locator("//input[@name='tz']").first
        id_input.fill(user_id_str)
        logger.info(">>> ID filled")

        password_input = target.locator("//input[@name='password']").first
        password_input.fill(user_password_str)
        logger.info(">>> Password filled")

        # Specific login button inside the modal
        # If inside a frame, the dialog container might be different or not present in the same way
        if frame:
             modal_login_button = target.locator("//button[text()='כניסה' and @type='button']").first
        else:
             modal_login_button = target.locator("//div[contains(@class, 'MuiDialog-container') and contains(@role, 'presentation')]//button[text()='כניסה' and @type='button']").first
             
        modal_login_button.click(force=True)
        logger.info(">>> Clicked login button in modal")

        try:
            if not frame:
                modal = target.locator("//div[contains(@class, 'MuiDialog-container') and contains(@role, 'presentation')]")
                modal.wait_for(state="hidden", timeout=10000)
                logger.info(">>> Modal closed successfully")
        except Exception:
            logger.warning(">>> Modal did NOT close – continue anyway")
