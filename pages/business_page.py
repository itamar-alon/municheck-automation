from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage 

class BusinessLicensePage(BasePage):
    """קלאס המייצג את דף רישוי העסקים ומכיל לוגיקת בדיקה מורכבת."""

    # --- Locators ונתוני בדיקה (ללא שינוי) ---
    GENERIC_LINK_BY_TEXT = (By.XPATH, "//a[.//text()[contains(.,'{}')]]")
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    
    # ⬅️ נתונים ספציפיים לעמוד רישוי עסקים (3 טאבים)
    TAB_BUTTON_NAME_2 = "דרישות ותנאים, מפרטים והיתרים"
    TAB_BUTTON_NAME_3 = "טפסים"
    TAB_2_URL_PART = "?tab=1" 
    TAB_3_URL_PART = "https://my.rishonlezion.muni.il/business/?tab=2" 

    # ⬅️ 1. קישורי בדיקה - טאב ברירת מחדל
    TAB_1_EXTERNAL_LINKS = {
        "שלבים בפתיחת עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/NewBusiness.aspx",
        "הגשת בקשה מקוונת לרישיון עסק": "por141.cityforms.co.il/ApplicationBuilder/eFormRender.html",
    }
    
    # ⬅️ 2. קישורי בדיקה - טאב פנימי שני
    TAB_2_EXTERNAL_LINKS = {
        "רישיון לניהול עסק": "rishonlezion.muni.il/Business/BusinessLicense/Pages/License.aspx", 
        "דרישות ותנאים לקבלת רישיון עסק": "rishonlezion.muni.il/Business/BusinessLicense/BusinessLicenseprocess/Pages/default.aspx",
        "אתר המפרטים האחידים ברישוי עסקים": "gov.il/he/departments/units/reform1/govil-landing-page",
        "בדיקת סטטוס רישוי": "city4u.co.il/PortalServicesSite/_portal/283000",
        "דרישות לנגישות עסקים": "rishonlezion.muni.il/Business/BusinessLicense/BusinessLicenseprocess/Pages/Accessibility.aspx",
    }
    
    # ⬅️ 3. קישורי בדיקה - טאב פנימי שלישי
    TAB_3_EXTERNAL_LINKS = {
        "בקשה להצבת כיסאות ושולחנות ומתקני תצוגה": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=8141005056A14F7F11CC002357F0A3B0&Process=TableAndChairsPermit141", 
        "תשלום להצבת שולחנות וכיסאות ו/או מתקני תצוגה": "city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/48",
        "בקשה לרישיון עסק מקוונת": "por141.cityforms.co.il/ApplicationBuilder/eFormRender.html",
        "בדיקת סטטוס רישוי עסק": "city4u.co.il/PortalServicesSite/_portal/283000",
        "תשלום אגרת רישוי עסק": "city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/118"
    }

    TAMAT_URL_PART = "CategoryID=3506"
    TAMAT_BUTTON_LOCATOR = (By.CSS_SELECTOR, f"a[href*='{TAMAT_URL_PART}']") 
    
    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    
    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = self.DEFAULT_WAIT_TIME 
        self.BUSINESS_URL = url 

    def open_business_page(self):
        """ מנווט ישירות לדף רישוי העסקים. """
        self.go_to_url(self.BUSINESS_URL)
        print(f">>> נווט לדף רישוי עסקים: {self.BUSINESS_URL}")

    def get_page_title(self):
        """ מחזיר את כותרת הדף (לצורך אימות). """
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    
    # --- מתודות עזר פנימיות ---

    def _get_link_locator(self, link_text):
        """ מחזיר את ה-Locator המתאים לקישור נתון. """
        if link_text == "רישום מעון חרצית תמ\"ת": 
             return self.TAMAT_BUTTON_LOCATOR 
        else:
             return (self.GENERIC_LINK_BY_TEXT[0], 
                     self.GENERIC_LINK_BY_TEXT[1].format(link_text))

    def _click_link_by_text(self, link_text):
        """ מבצעת את הלחיצה על קישור ספציפי באמצעות JavaScript. """
        dynamic_locator = self._get_link_locator(link_text)
        link_element = self.wait_for_clickable_element(dynamic_locator, timeout=self.DEFAULT_TIMEOUT) 
        self.execute_script("arguments[0].click();", link_element)
        print(f">>> נשלחה פקודת לחיצת JavaScript על '{link_text}'.")


    def _verify_single_external_link_navigation(self, link_text, expected_url_part):
        """ פונקציה פנימית: לוחצת, עוברת טאב, מאמת URL וחוזרת (בדיקה יחידה). """
        print(f"\n--- מתחיל בדיקת ניווט: {link_text} ---")

        original_window = self.driver.current_window_handle
        
        self._click_link_by_text(link_text)
        
        # 🟢 המתנה מפורשת לפתיחת חלון חדש (במקום לולאה עם sleep)
        try:
            WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.number_of_windows_to_be(2)
            )
            print(">>> בוצעה המתנה לחלון חדש.")
        except TimeoutException:
            raise TimeoutException(f"❌ לא נפתח טאב חדש תוך {self.DEFAULT_TIMEOUT} שניות לאחר הלחיצה על '{link_text}'.")
            
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)
        print(">>> בוצע מעבר לטאב החדש.")

        # המתנה לטעינת ה-URL
        self.wait_for_url_to_contain(expected_url_part, timeout=15)
        
        final_url = self.driver.current_url
        assert expected_url_part in final_url, f"❌ הניווט לא הוביל לכתובת החיצונית הנכונה! נמצא: {final_url}"
        
        print(f"✅ אימות ניווט ל'{link_text}' עבר בהצלחה. כתובת יעד: {final_url}")

        self.driver.close()
        self.driver.switch_to.window(original_window)
        print(">>> חזרה לטאב המקורי. הבדיקה מוכנה להמשך.")

    # --- מתודות Flow ציבוריות (הכוללות את המתודות החסרות) ---

    def run_tab_1_external_link_tests(self):
        """ מריץ לולאה על כל הקישורים החיצוניים בטאב ברירת המחדל. """
        print("\n--- מתחיל בדיקת קישורים חיצוניים (טאב ברירת מחדל) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print("--- סיום בדיקת קישורים חיצוניים (טאב ברירת מחדל) ---")


    def navigate_to_tab_2(self):
        """ 🟢 תיקון: שימוש ב-wait_for_invisibility לייצוב מעבר טאב 2. """
        print(f"\n--- מתחיל ניווט לטאב: {self.TAB_BUTTON_NAME_2} ---")
        
        tab_locator = (self.GENERIC_TAB_BUTTON[0], 
                       self.GENERIC_TAB_BUTTON[1].format(self.TAB_BUTTON_NAME_2))
        
        tab_element = self.wait_for_clickable_element(tab_locator, timeout=self.DEFAULT_TIMEOUT)

        # 1. 🟢 שמירת מיקום האלמנט הישן (האלמנט הראשון בטאב 1)
        first_link_tab_1 = list(self.TAB_1_EXTERNAL_LINKS.keys())[0] 
        old_dynamic_locator = self._get_link_locator(first_link_tab_1) 
        
        # 2. לחיצה באמצעות Selenium
        tab_element.click() 
        print(f">>> בוצעה לחיצת Selenium על טאב '{self.TAB_BUTTON_NAME_2}'.")
        
        # 3. 🟢 המתנה להיעלמות האלמנט הישן (כדי לוודא שהטאב התחלף)
        try:
            self.wait_for_invisibility(old_dynamic_locator, timeout=self.DEFAULT_TIMEOUT)
            print(">>> האלמנטים בטאב הישן נעלמו (DOM התעדכן).")
        except TimeoutException:
            pass

        # 4. המתנה ליציבות DOM (מחכים לקישור הראשון בטאב 2 שיופיע)
        first_link_name = list(self.TAB_2_EXTERNAL_LINKS.keys())[0] 
        dynamic_locator = self._get_link_locator(first_link_name) 
        
        self.wait_for_clickable_element(dynamic_locator, timeout=self.DEFAULT_TIMEOUT)
        print(">>> האלמנטים בטאב החדש יציבים ומוכנים ללחיצה.") 

        # 5. המתנה מפורשת לשינוי URL (לאחר טעינת האלמנטים)
        self.wait_for_url_to_contain(self.TAB_2_URL_PART, timeout=self.DEFAULT_TIMEOUT)
        
        final_url = self.driver.current_url
        if self.TAB_2_URL_PART not in final_url:
              raise Exception(f"❌ ה-URL הפנימי לא השתנה כצפוי! נמצא: {final_url}")
              
        print(f"✅ ניווט פנימי לטאב '{self.TAB_BUTTON_NAME_2}' עבר בהצלחה. URL: {final_url}")


    def run_tab_2_external_link_tests(self):
        """ מריץ לולאה על כל הקישורים החיצוניים בטאב הפנימי השני. """
        print(f"\n--- מתחיל בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME_2}) ---")
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- סיום בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME_2}) ---")


    def navigate_to_tab_3(self):
        """ 🟢 תיקון: שימוש ב-wait_for_invisibility לייצוב מעבר טאב 3. """
        print(f"\n--- מתחיל ניווט לטאב: {self.TAB_BUTTON_NAME_3} ---")
        
        tab_locator = (self.GENERIC_TAB_BUTTON[0], 
                       self.GENERIC_TAB_BUTTON[1].format(self.TAB_BUTTON_NAME_3))
        
        tab_element = self.wait_for_clickable_element(tab_locator, timeout=self.DEFAULT_TIMEOUT) 

        # 1. 🟢 שמירת מיקום האלמנט הישן (האלמנט הראשון בטאב 2 - אליו הגענו קודם)
        first_link_tab_2 = list(self.TAB_2_EXTERNAL_LINKS.keys())[0] 
        old_dynamic_locator = self._get_link_locator(first_link_tab_2) 
        
        # 2. לחיצה באמצעות Selenium
        tab_element.click() 
        print(f">>> בוצעה לחיצת Selenium על טאב '{self.TAB_BUTTON_NAME_3}'.")
        
        # 3. 🟢 המתנה להיעלמות האלמנט הישן
        try:
            self.wait_for_invisibility(old_dynamic_locator, timeout=self.DEFAULT_TIMEOUT)
            print(">>> האלמנטים בטאב הישן נעלמו (DOM התעדכן).")
        except TimeoutException:
            pass

        # 4. המתנה ליציבות DOM (מחכים לקישור הראשון בטאב 3 שיופיע)
        first_link_name = list(self.TAB_3_EXTERNAL_LINKS.keys())[0] 
        new_dynamic_locator = self._get_link_locator(first_link_name) 
        
        self.wait_for_clickable_element(new_dynamic_locator, timeout=self.DEFAULT_TIMEOUT)
        print(">>> האלמנטים בטאב החדש יציבים ומוכנים ללחיצה.") 

        # 5. המתנה מפורשת לשינוי URL (לאחר טעינת האלמנטים)
        self.wait_for_url_to_contain(self.TAB_3_URL_PART, timeout=self.DEFAULT_TIMEOUT)
        
        final_url = self.driver.current_url
        if self.TAB_3_URL_PART not in final_url:
              raise Exception(f"❌ ה-URL הפנימי לא השתנה כצפוי! נמצא: {final_url}")
              
        print(f"✅ ניווט פנימי לטאב '{self.TAB_BUTTON_NAME_3}' עבר בהצלחה. URL: {final_url}")


    def run_tab_3_external_link_tests(self):
        """ מריץ לולאה על כל הקישורים החיצוניים בטאב הפנימי השלישי. """
        print(f"\n--- מתחיל בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME_3}) ---")
        for link_name, url_part in self.TAB_3_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- סיום בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME_3}) ---")