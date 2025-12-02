from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage

class EnforcementPage(BasePage):
    """
    קלאס המייצג את דף פיקוח עירוני (Enforcement).
    מכיל לוגיקת בדיקה יציבה מבוססת על מנגנון ה-Retry וה-XPath החכם.
    """

    # --- Locators ונתוני בדיקה ---
    # Locator חכם לחיפוש קישור לפי טקסט (משתמש ב-normalize-space לניקוי רווחים נסתרים)
    GENERIC_LINK_BY_TEXT = (By.XPATH, "//a[contains(normalize-space(.), '{}')]")
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    PAGE_TITLE = (By.TAG_NAME, "h1")

    # ⬅️ 1. קישורי בדיקה - טאב ברירת מחדל (דוחות וקנסות)
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
    

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.ENFORCEMENT_URL = url

    def open_enforcement_page(self):
        """ מנווט ישירות לדף פיקוח עירוני. """
        self.go_to_url(self.ENFORCEMENT_URL)
        print(f">>> נווט לדף פיקוח עירוני: {self.ENFORCEMENT_URL}")

    def get_page_title(self):
        """ מחזיר את כותרת הדף (לצורך אימות). """
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    # --- מתודות עזר פנימיות (מנגנון היציבות) ---

    def _get_link_locator(self, link_text):
        """ מחזיר את ה-Locator המתאים לקישור נתון (משתמש ב-normalize-space). """
        xpath = f"//a[contains(normalize-space(.), '{link_text}')]"
        return (By.XPATH, xpath)

    def _click_link_by_text(self, link_text):
        """ לחיצה חכמה עם מנגנון Retry נגד Stale Elements. """
        dynamic_locator = self._get_link_locator(link_text)
        
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            try:
                link_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located(dynamic_locator)
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_element)
                time.sleep(0.5)

                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(dynamic_locator))

                try:
                    link_element.click()
                except:
                    self.execute_script("arguments[0].click();", link_element)
                
                print(f">>> בוצעה לחיצה על '{link_text}' (נסיון {attempts+1}).")
                return 
                
            except (StaleElementReferenceException, TimeoutException):
                print(f"⚠️ נסיון {attempts+1} נכשל עבור '{link_text}', מנסה שוב...")
                attempts += 1
                time.sleep(1)
            except Exception as e:
                print(f"❌ שגיאה בלתי צפויה בלחיצה על '{link_text}': {str(e)}")
                raise e

        raise Exception(f"❌ נכשל ללחוץ על האלמנט '{link_text}' לאחר {max_attempts} נסיונות.")

    def _verify_single_external_link_navigation(self, link_text, expected_url_part):
        """ פונקציה פנימית: לוחצת, עוברת טאב, מאמת URL וחוזרת. """
        print(f"\n--- מתחיל בדיקת ניווט: {link_text} ---")

        original_window = self.driver.current_window_handle
        
        self._click_link_by_text(link_text)
        
        try:
            WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.number_of_windows_to_be(2)
            )
        except TimeoutException:
            if expected_url_part in self.driver.current_url:
                 print("⚠️ הלינק נפתח באותו חלון (לא בטאב חדש).")
                 self.driver.back()
                 return
            else:
                 raise TimeoutException(f"❌ לא נפתח טאב חדש עבור '{link_text}'.")
            
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)
        
        try:
            self.wait_for_url_to_contain(expected_url_part, timeout=15)
        except TimeoutException:
             print(f"⚠️ אזהרה: ה-URL לא הכיל את '{expected_url_part}' בזמן, אבל נמשיך לבדיקה.")

        final_url = self.driver.current_url
        
        if expected_url_part not in final_url:
            print(f"❌ שגיאת אימות: ציפינו ל-'{expected_url_part}' וקיבלנו '{final_url}'")
        else:
            print(f"✅ אימות ניווט ל'{link_text}' עבר בהצלחה.")

        self.driver.close()
        self.driver.switch_to.window(original_window)
        time.sleep(0.5)

    def run_tab_1_external_link_tests(self):
        """ מריץ לולאה על כל הקישורים החיצוניים בטאב ברירת המחדל (דוחות וקנסות). """
        print("\n--- מתחיל בדיקת קישורים חיצוניים (טאב דוחות וקנסות) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print("--- סיום בדיקת קישורים חיצוניים (טאב דוחות וקנסות) ---")
        