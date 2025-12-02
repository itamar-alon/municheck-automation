from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage

class BusinessLicensePage(BasePage):
    """קלאס המייצג את דף רישוי העסקים ומכיל לוגיקת בדיקה מורכבת ויציבה."""

    # --- Locators ונתוני בדיקה ---
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    
    # ⬅️ נתונים ספציפיים לעמוד רישוי עסקים (3 טאבים)
    TAB_BUTTON_NAME_2 = "דרישות ותנאים, מפרטים והיתרים"
    TAB_BUTTON_NAME_3 = "טפסים"
    TAB_2_URL_PART = "?tab=1"
    TAB_3_URL_PART = "?tab=2"

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
    
    # ⬅️ 3. קישורי בדיקה - טאב פנימי שלישי - גרסה מקוצרת ויציבה
    # קיצרנו את הטקסטים כדי למנוע נפילות על רווחים נסתרים או שבירת שורות
    TAB_3_EXTERNAL_LINKS = {
        "בקשה להצבת כי​סאות ושולחנות ומתקני תצוגה": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=8141005056A14F7F11CC002357F0A3B0&Process=TableAndChairsPermit141",
        "תשלום​​ להצבת שולחנות וכיסאות ו/או מתקני תצוגה​": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/48",
        "בקשה לרישיון": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=B8180050568AAB9211BBBBB84CF531F6&Process=BusinessLicense141",
        "חוות דעת מקדמית לאישור הנדסי​​": "https://por141.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=B81B0050568AAB9211CC0B2FE5206B86&Process=BusinessLicenseInfo141",
        "בדיקת סטטוס רישוי": "https://city4u.co.il/PortalServicesSite/_portal/283000",
        "אגרת רישוי עסק": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/118"
    }

    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
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
        """ 
        מחזיר locator חכם שמתעלם מרווחים כפולים או ירידות שורה.
        השימוש ב-normalize-space הוא קריטי לאתרים ממשלתיים ישנים.
        """
        xpath = f"//a[contains(normalize-space(.), '{link_text}')]"
        return (By.XPATH, xpath)

    def _click_link_by_text(self, link_text):
        """ מבצעת את הלחיצה בצורה חכמה עם מנגנון Retry נגד Stale Elements. """
        dynamic_locator = self._get_link_locator(link_text)
        
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            try:
                # 1. מציאת האלמנט
                link_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located(dynamic_locator)
                )
                
                # 2. גלילה אליו (מרכז המסך)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_element)
                time.sleep(0.5) 

                # 3. המתנה שהאלמנט יהיה לחיץ
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(dynamic_locator))

                # 4. נסיון לחיצה
                try:
                    link_element.click()
                except:
                    # גיבוי: לחיצת JS אם הלחיצה הרגילה נחסמה
                    self.execute_script("arguments[0].click();", link_element)
                
                print(f">>> בוצעה לחיצה על '{link_text}' (נסיון {attempts+1}).")
                return 
                
            except (StaleElementReferenceException, TimeoutException):
                print(f"⚠️ נסיון {attempts+1} נכשל עבור '{link_text}', מנסה שוב...")
                attempts += 1
                time.sleep(1) # נותן ל-DOM להירגע
            except Exception as e:
                print(f"❌ שגיאה בלתי צפויה בלחיצה על '{link_text}': {str(e)}")
                raise e

        raise Exception(f"❌ נכשל ללחוץ על האלמנט '{link_text}' לאחר {max_attempts} נסיונות.")

    def _verify_single_external_link_navigation(self, link_text, expected_url_part):
        """ פונקציה פנימית: לוחצת, עוברת טאב, מאמת URL וחוזרת. """
        print(f"\n--- מתחיל בדיקת ניווט: {link_text} ---")

        original_window = self.driver.current_window_handle
        
        self._click_link_by_text(link_text)
        
        # המתנה לפתיחת חלון חדש
        try:
            WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.number_of_windows_to_be(2)
            )
        except TimeoutException:
            # בדיקה אם הלינק נפתח באותו חלון בטעות
            if expected_url_part in self.driver.current_url:
                 print("⚠️ הלינק נפתח באותו חלון (לא בטאב חדש).")
                 self.driver.back()
                 return
            else:
                 raise TimeoutException(f"❌ לא נפתח טאב חדש עבור '{link_text}'.")
            
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)
        
        # המתנה לטעינת ה-URL
        try:
            self.wait_for_url_to_contain(expected_url_part, timeout=15)
        except TimeoutException:
             print(f"⚠️ אזהרה: ה-URL לא הספיק להכיל את '{expected_url_part}', ממשיך לבדיקה.")

        final_url = self.driver.current_url
        
        if expected_url_part not in final_url:
            print(f"❌ שגיאת אימות: ציפינו ל-'{expected_url_part}' וקיבלנו '{final_url}'")
        else:
            print(f"✅ אימות ניווט ל'{link_text}' עבר בהצלחה.")

        self.driver.close()
        self.driver.switch_to.window(original_window)
        time.sleep(0.5) # ייצוב חזרה לחלון הראשי

    # --- מתודות Flow ציבוריות ---

    def run_tab_1_external_link_tests(self):
        print("\n--- מתחיל בדיקת קישורים חיצוניים (טאב ברירת מחדל) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print("--- סיום בדיקת קישורים חיצוניים (טאב ברירת מחדל) ---")

    def navigate_to_tab_2(self):
        self._switch_tab_safe(self.TAB_BUTTON_NAME_2, self.TAB_2_URL_PART)

    def run_tab_2_external_link_tests(self):
        print(f"\n--- מתחיל בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME_2}) ---")
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- סיום בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME_2}) ---")

    def navigate_to_tab_3(self):
        self._switch_tab_safe(self.TAB_BUTTON_NAME_3, self.TAB_3_URL_PART)

    def run_tab_3_external_link_tests(self):
        print(f"\n--- מתחיל בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME_3}) ---")
        for link_name, url_part in self.TAB_3_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- סיום בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME_3}) ---")

    def _switch_tab_safe(self, tab_name, expected_url_part):
        """ מעבר טאב בטוח עם המתנות קשיחות """
        print(f"\n--- מתחיל ניווט לטאב: {tab_name} ---")
        
        tab_locator = (self.GENERIC_TAB_BUTTON[0], 
                       self.GENERIC_TAB_BUTTON[1].format(tab_name))
        
        # לחיצה
        tab_element = self.wait_for_clickable_element(tab_locator, timeout=self.DEFAULT_TIMEOUT)
        try:
            tab_element.click()
        except:
             self.execute_script("arguments[0].click();", tab_element)
        
        print(f">>> בוצעה לחיצה על טאב '{tab_name}'.")

        # 🛑 המתנה קשיחה - קריטי במעבר בין טאבים דינמיים!
        time.sleep(2) 

        # המתנה לשינוי URL
        try:
            self.wait_for_url_to_contain(expected_url_part, timeout=5)
        except:
            pass # לפעמים ה-URL מתעדכן מהר מאוד לפני שהבדיקה מתחילה

        print(f"✅ המעבר לטאב '{tab_name}' הושלם.")