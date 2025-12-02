from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By 

class BasePage:
    """ מחלקת בסיס המכילה פעולות נפוצות של Selenium (המתנה, לחיצה, חיפוש, ניווט). """
    
    DEFAULT_WAIT_TIME = 10
    
    # 🛑 תיקון קריטי: הפיכת driver לאופציונלי (None)
    def __init__(self, driver=None):
        self.driver = driver
        
        # 🟢 ייצוב: יוצרים את ה-wait רק אם ה-driver סופק
        if driver:
            self.wait = WebDriverWait(driver, self.DEFAULT_WAIT_TIME)
        else:
            self.wait = None # או שתטפל בזה במקום אחר, אך כרגע נגדיר כ-None

    def _get_wait(self, timeout):
        """ מחזיר אובייקט WebDriverWait עם ה-timeout הרצוי. """
        # אם ה-driver לא אופסן ב-init, זה יקרוס. לכן אנו נשתמש ב-WebDriverWait חדש.
        if self.driver is None:
            raise Exception("Driver object must be initialized before performing wait operations.")

        if timeout is None:
            # במקום להשתמש ב-self.wait הבעייתי, אנו יוצרים אותו מחדש כאן
            return WebDriverWait(self.driver, self.DEFAULT_WAIT_TIME) 
        
        return WebDriverWait(self.driver, timeout)

    def execute_script(self, script, element=None):
        """ מבצע קוד JavaScript על הדרייבר או אלמנט ספציפי. """
        if element:
            self.driver.execute_script(script, element)
        else:
            self.driver.execute_script(script)
    
    # --- פעולות בסיסיות לניווט ---
    
    def go_to_url(self, url):
        """ מנווט לכתובת URL נתונה """
        self.driver.get(url)
        
    # --- פעולות בסיסיות לאלמנטים ---
    
    def click(self, by_locator, timeout=None):
        """ מחפש אלמנט ולוחץ עליו בצורה יציבה. """
        self._get_wait(timeout).until(EC.element_to_be_clickable(by_locator)).click()
    
    def enter_text(self, by_locator, text, timeout=None):
        """ מחפש אלמנט ומזין טקסט. """
        element = self.get_element(by_locator, timeout=timeout)
        element.send_keys(text)
        
    # --- פעולות המתנה והשגה (Get) מורחבות ---
    
    def get_element(self, by_locator, timeout=None):
        """ ממתין עד שהאלמנט קיים ב-DOM ומחזיר אותו. """
        return self._get_wait(timeout).until(EC.presence_of_element_located(by_locator))
    
    def wait_for_clickable_element(self, by_locator, timeout=None):
        """ ממתין עד שהאלמנט ניתן ללחיצה ומחזיר אותו. """
        return self._get_wait(timeout).until(EC.element_to_be_clickable(by_locator))
    
    def wait_for_invisibility(self, by_locator, timeout=None):
        """ ממתין עד שהאלמנט נעלם. """
        if timeout is None:
            timeout = 30 # זמן ארוך יותר ליציבות
        WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(by_locator))
    
    def wait_for_url_to_contain(self, url_part, timeout=None):
        """ ממתין עד שה-URL מכיל חלק מסוים. """
        if timeout is None:
            timeout = 15
        WebDriverWait(self.driver, timeout).until(EC.url_contains(url_part))