from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By 


class BasePage:
    """ מחלקת בסיס המכילה פעולות נפוצות של Selenium (המתנה, לחיצה, חיפוש, ניווט). """
    
    DEFAULT_WAIT_TIME = 10
    
    def __init__(self, driver=None):
        self.driver = driver
        
        if driver:
            self.wait = WebDriverWait(driver, self.DEFAULT_WAIT_TIME)
        else:
            self.wait = None


    def _get_wait(self, timeout):
        """ מחזיר אובייקט WebDriverWait עם timeout מותאם. """
        if self.driver is None:
            raise Exception("Driver object must be initialized before performing wait operations.")

        if timeout is None:
            return WebDriverWait(self.driver, self.DEFAULT_WAIT_TIME)
        
        return WebDriverWait(self.driver, timeout)


    def execute_script(self, script, element=None):
        """ מבצע JavaScript על אלמנט או על הדפדפן. """
        if element:
            return self.driver.execute_script(script, element)
        return self.driver.execute_script(script)
    

    # --- ניווט ---

    def go_to_url(self, url):
        self.driver.get(url)


    # --- פעולות בסיסיות ---

    def click(self, by_locator, timeout=None):
        self._get_wait(timeout).until(EC.element_to_be_clickable(by_locator)).click()
    

    def enter_text(self, by_locator, text, timeout=None):
        element = self.get_element(by_locator, timeout=timeout)
        element.clear()
        element.send_keys(text)

        # 🔵 בדיקה שהערך אכן נכנס — נדרש בשביל React
        if element.get_attribute("value") != text:
            self.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles:true }));",
                element, text
            )


    # --- פעולות השגה והמתנה ---

    # 🔵 קריטי — React דורש שהאלמנט יהיה *נראה* (לא רק קיים ב-DOM)
    def get_element(self, by_locator, timeout=None):
        return self._get_wait(timeout).until(
            EC.visibility_of_element_located(by_locator)
        )


    def wait_for_clickable_element(self, by_locator, timeout=None):
        return self._get_wait(timeout).until(
            EC.element_to_be_clickable(by_locator)
        )
    

    def wait_for_invisibility(self, by_locator, timeout=None):
        """ המתנה אמיתית להיעלמות — כולל fallback ל-opacity """
        if timeout is None:
            timeout = 30
        
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.invisibility_of_element_located(by_locator))
            return
        except TimeoutException:
            pass

        # 🔵 fallback — React לעיתים משאיר אלמנט חי אבל שקוף
        try:
            wait.until(
                lambda d: d.find_element(*by_locator).value_of_css_property("opacity") == "0"
            )
        except Exception:
            raise TimeoutException(f"Element {by_locator} is still visible after {timeout} seconds.")


    def wait_for_url_to_contain(self, url_part, timeout=None):
        if timeout is None:
            timeout = 15

        WebDriverWait(self.driver, timeout).until(EC.url_contains(url_part))


    def wait_for_visible(self, by_locator, timeout=None):
        """ ממתין שהאלמנט נראה על המסך וגם קיים ב-DOM """
        return self._get_wait(timeout).until(
            EC.visibility_of_element_located(by_locator)
        )