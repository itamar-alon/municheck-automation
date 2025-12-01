from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By 

class BasePage:
    """ מחלקת בסיס המכילה פעולות נפוצות של Selenium (המתנה, לחיצה, חיפוש, ניווט). """
    
    DEFAULT_WAIT_TIME = 10
    
    def __init__(self, driver):
        self.driver = driver
        # ⚠️ הפעלת WebDriverWait חדש בכל קריאה ל-wait_for... (במקום לאחסן אותו במשתנה סלף)
        # זה מבטיח שאנו יכולים להשתמש ב-timeout דינמי
        # נשאיר את זה כפי שהיה במקור כי רוב המתודות משתמשות ב-self.wait
        self.wait = WebDriverWait(driver, self.DEFAULT_WAIT_TIME)

    def _get_wait(self, timeout):
        """ מחזיר אובייקט WebDriverWait עם ה-timeout הרצוי. """
        if timeout is None:
            return self.wait # משתמש בזמן ברירת המחדל
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
        """ 🟢 תיקון: הוספת timeout אופציונלי. מחפש אלמנט ולוחץ עליו בצורה יציבה. """
        self._get_wait(timeout).until(EC.element_to_be_clickable(by_locator)).click()
    
    def enter_text(self, by_locator, text, timeout=None):
        """ 🟢 תיקון: הוספת timeout אופציונלי. מחפש אלמנט ומזין טקסט. """
        element = self.get_element(by_locator, timeout=timeout)
        element.send_keys(text)
        
    # --- פעולות המתנה והשגה (Get) מורחבות ---
    
    def get_element(self, by_locator, timeout=None):
        """ 🟢 תיקון: הוספת timeout אופציונלי. ממתין עד שהאלמנט קיים ב-DOM ומחזיר אותו. """
        return self._get_wait(timeout).until(EC.presence_of_element_located(by_locator))
    
    def wait_for_clickable_element(self, by_locator, timeout=None):
        """ 🟢 תיקון קריטי: הוספת timeout אופציונלי. ממתין עד שהאלמנט ניתן ללחיצה ומחזיר אותו. """
        return self._get_wait(timeout).until(EC.element_to_be_clickable(by_locator))
    
    def wait_for_invisibility(self, by_locator, timeout=None):
        """ 🟢 תיקון: הוספת timeout אופציונלי. ממתין עד שהאלמנט נעלם. """
        # כאן נשמור את ברירת המחדל ל-30 שניות רק כדי לא לשבור את הממשק המקורי שלך
        if timeout is None:
            timeout = 30
        WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(by_locator))
    
    def wait_for_url_to_contain(self, url_part, timeout=None):
        """ 🟢 תיקון: הוספת timeout אופציונלי. ממתין עד שה-URL מכיל חלק מסוים. """
        if timeout is None:
            timeout = 15
        WebDriverWait(self.driver, timeout).until(EC.url_contains(url_part))