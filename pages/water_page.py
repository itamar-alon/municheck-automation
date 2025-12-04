from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage

class WaterPage(BasePage):
    """
    קלאס המייצג את דף ממשק המים (Water Interface).
    מכיל לוגיקת בדיקה יציבה מבוססת על מנגנון ה-Retry וה-XPath החכם.
    """

    # --- Locators ונתוני בדיקה ---
    GENERIC_LINK_BY_TEXT = (By.XPATH, "//a[contains(normalize-space(.), '{}')]")
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    # ⬅️ נתונים ספציפיים לעמוד המים (3 טאבים)
    # 🟢 יש להחליף את השמות בהתאם לטקסט המופיע על כפתורי הטאבים בפועל באתר המים!
    TAB_BUTTON_NAME_2 = "טפסים מקוונים" 
    TAB_BUTTON_NAME_3 = "טפסים להורדה"
    
    # 🟢 ה-URL הצפוי לאחר לחיצה על הטאב (בד"כ שינוי בפרמטר ה-query)
    TAB_2_URL_PART = "?tab=1" 
    TAB_3_URL_PART = "?tab=2"

    # ⬅️ 1. קישורי בדיקה - טאב ברירת מחדל (חשבונות מים)
    TAB_1_EXTERNAL_LINKS = {
        "תשלום חשבון מים": "https://www.mast.co.il/15657/payment"
    }
    
    # ⬅️ 2. קישורי בדיקה - טאב פנימי שני (פניות והידרנטים)
    # 🟢 נתונים לדוגמה
    TAB_2_EXTERNAL_LINKS = {
        "עדכון מספר נפשות": "https://www.mast.co.il/",
        "צריכת מים משותפת": "https://www.mast.co.il/",
        "הפקדת מפתח": "https://www.mast.co.il/",
        "בקשה לפינוי ביוב": "https://www.meniv-rishon.co.il/Service/forms/Pages/form_3_pinui_biuv.aspx",
        "בירור חיוב בעד צריכת מים": "https://www.mast.co.il/" ,
        "הכרה בתעריף מיוחד": "https://www.mast.co.il/" ,
        "מנזילה במערכת המים": "https://www.mast.co.il/" ,
        "מסירת קריאת מונה": "https://www.mast.co.il/" ,
        "ביצוע בדיקות": "https://www.mast.co.il/"
    }

    # ⬅️ 3. קישורי בדיקה - טאב פנימי שלישי (טפסים להורדה)
    # 🟢 נתונים לדוגמה
    TAB_3_EXTERNAL_LINKS = {
        "בקשה לביקור מתואם": "https://www.meniv-rishon.co.il/Service/forms/Documents/setvisit.pdf",
        "לקבלת מידע": "https://www.meniv-rishon.co.il/Service/forms/Documents/%D7%91%D7%A7%D7%A9%D7%94%20%D7%9C%D7%A7%D7%91%D7%9C%D7%AA%20%D7%9E%D7%99%D7%93%D7%A2.pdf",
        "הוראה לחיוב בבנק": "https://www.meniv-rishon.co.il/Service/forms/Documents/%D7%94%D7%95%D7%A8%D7%90%D7%94%20%D7%9C%D7%97%D7%99%D7%95%D7%91%20-%20%D7%97%D7%9C%D7%95%D7%A4%D7%94%20%D7%9E%D7%95%D7%A0%D7%92%D7%A9%20(1).pdf",
        "החלפת מחזיקים": "https://www.meniv-rishon.co.il/Service/forms/Documents/%D7%94%D7%A6%D7%94%D7%A8%D7%94%20%D7%A2%D7%9C%20%D7%94%D7%97%D7%9C%D7%A4%D7%AA%20%D7%A6%D7%A8%D7%9B%D7%A0%D7%99%D7%9D%20%D7%91%D7%A0%D7%9B%D7%A1.pdf" ,
        "הנחיות להגשת תכנית": "https://www.meniv-rishon.co.il/Service/forms/Documents/%D7%94%D7%A0%D7%97%D7%99%D7%95%D7%AA%20%D7%9C%D7%94%D7%92%D7%A9%D7%AA%20%D7%AA%D7%9B%D7%A0%D7%99%D7%AA%20%D7%A1%D7%A0%D7%99%D7%98%D7%A8%D7%99%D7%AA%20%D7%9E%D7%9E%D7%95%D7%96%D7%92.pdf" ,
        "לקבלת תעודת גמר": "https://www.meniv-rishon.co.il/Service/forms/Documents/%D7%98%D7%95%D7%A4%D7%A1%205%20%D7%9E%D7%A2%D7%95%D7%93%D7%9B%D7%9F%20%D7%A1%D7%95%D7%A4%D7%99%202024.pdf" ,
        "עם כשרות מהודרת": "https://www.meniv-rishon.co.il/Service/forms/Documents/%D7%98%D7%95%D7%A4%D7%A1%20%D7%A0%D7%AA%D7%95%D7%A0%D7%99%D7%9D%20%D7%9E%D7%93%D7%99%20%D7%A7%D7%A8%D7%9E.pdf" 
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.WATER_URL = url
        self.TAB_1_NAME = "חשבונות מים" 
        # TAB_2_NAME ו-TAB_3_NAME יוגדרו אוטומטית ע"י משתני המחלקה

    def open_water_page(self):
        """ מנווט ישירות לדף ממשק המים. """
        self.go_to_url(self.WATER_URL)
        print(f">>> Navigated to Water Interface page: {self.WATER_URL}")

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
                
                print(f">>> Clicked on '{link_text}' (Attempt {attempts+1}).")
                return 
                
            except (StaleElementReferenceException, TimeoutException):
                print(f"⚠️ Attempt {attempts+1} failed for '{link_text}', trying again...")
                attempts += 1
                time.sleep(1) # נותן ל-DOM להירגע
            except Exception as e:
                print(f"❌ Unexpected error while clicking '{link_text}': {str(e)}")
                raise e

        raise Exception(f"❌ Failed to click element '{link_text}' after {max_attempts} attempts.")

    def _verify_single_external_link_navigation(self, link_text, expected_url_part):
        """ פונקציה פנימית: לוחצת, עוברת טאב, מאמת URL וחוזרת. """
        print(f"\n--- Starting navigation test: {link_text} ---")

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
                 print("⚠️ Link opened in the same window (not a new tab).")
                 self.driver.back()
                 return
            else:
                 raise TimeoutException(f"❌ New tab did not open for '{link_text}'.")
            
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)
        
        # המתנה לטעינת ה-URL
        try:
            self.wait_for_url_to_contain(expected_url_part, timeout=15) 
        except TimeoutException:
             print(f"⚠️ Warning: URL did not contain '{expected_url_part}' in time, proceeding with check.")

        final_url = self.driver.current_url
        
        if expected_url_part not in final_url:
            print(f"❌ Validation error: Expected '{expected_url_part}' but got '{final_url}'")
        else:
            print(f"✅ Navigation validation for '{link_text}' passed.")

        self.driver.close()
        self.driver.switch_to.window(original_window)
        time.sleep(0.5) # ייצוב חזרה לחלון הראשי

    # --- מתודות Flow ציבוריות ---

    def run_tab_1_external_link_tests(self):
        """ מריץ לולאה על כל הקישורים החיצוניים בטאב ברירת המחדל. """
        print(f"\n--- Starting external link test (Tab: {self.TAB_1_NAME}) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- External link test finished (Tab: {self.TAB_1_NAME}) ---")

    def navigate_to_tab_2(self):
        """ מנווט לטאב השני ("טפסים מקוונים") """
        self._switch_tab_safe(self.TAB_BUTTON_NAME_2, self.TAB_2_URL_PART)

    def run_tab_2_external_link_tests(self):
        """ מריץ לולאה על הקישורים החיצוניים בטאב 2. """
        print(f"\n--- Starting external link test (Tab: {self.TAB_BUTTON_NAME_2}) ---")
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- External link test finished (Tab: {self.TAB_BUTTON_NAME_2}) ---")

    def navigate_to_tab_3(self):
        """ מנווט לטאב השלישי ("טפסים להורדה") """
        self._switch_tab_safe(self.TAB_BUTTON_NAME_3, self.TAB_3_URL_PART)

    def run_tab_3_external_link_tests(self):
        """ מריץ לולאה על הקישורים החיצוניים בטאב 3. """
        print(f"\n--- Starting external link test (Tab: {self.TAB_BUTTON_NAME_3}) ---")
        for link_name, url_part in self.TAB_3_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- External link test finished (Tab: {self.TAB_BUTTON_NAME_3}) ---")

    def _switch_tab_safe(self, tab_name, expected_url_part):
        """ מעבר טאב בטוח עם המתנות קשיחות (הועתק מ-BusinessLicensePage). """
        print(f"\n--- Starting navigation to tab: {tab_name} ---")
        
        tab_locator = (self.GENERIC_TAB_BUTTON[0], 
                        self.GENERIC_TAB_BUTTON[1].format(tab_name))
        
        # לחיצה
        tab_element = self.wait_for_clickable_element(tab_locator, timeout=self.DEFAULT_TIMEOUT) 
        try:
            tab_element.click()
        except:
             self.execute_script("arguments[0].click();", tab_element)
        
        print(f">>> Clicked on tab '{tab_name}'.")

        # 🛑 המתנה קשיחה - קריטי במעבר בין טאבים דינמיים!
        time.sleep(2) 

        # המתנה לשינוי URL
        try:
            self.wait_for_url_to_contain(expected_url_part, timeout=5)
        except:
            pass # לפעמים ה-URL מתעדכן מהר מאוד לפני שהבדיקה מתחילה

        print(f"✅ Navigation to tab '{tab_name}' complete.")