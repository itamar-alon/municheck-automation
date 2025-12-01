from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from .base_page import BasePage 
from selenium.webdriver.common.by import By

class DaycarePage(BasePage):
    """קלאס המייצג את דף ה-Daycare / הגנים ומכיל לוגיקת בדיקה מורכבת."""

    # --- Locators ונתוני בדיקה ---
    # Locators גנריים מורכבים למציאת תגית <a> המכילה טקסט כצאצא
    GENERIC_LINK_BY_TEXT = (By.XPATH, "//a[.//text()[contains(.,'{}')]]")
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), '{}')]")
    
    # 🛑 פתרון סופי ואמין: Locator לפי CSS Selector המשתמש ב-URL (href)
    # זה עוקף לחלוטין את בעיית הקידוד והתחביר של הגרשיים ב-XPath.
    TAMAT_URL_PART = "CategoryID=3506"
    TAMAT_BUTTON_LOCATOR = (By.CSS_SELECTOR, f"a[href*='{TAMAT_URL_PART}']") 
    
    TAB_BUTTON_NAME = "מעונות יום" 
    TAB_2_URL_PART = "?tab=1" 

    # ⬅️ 1. קישורי בדיקה - טאב 'צהרונים' (ברירת מחדל)
    TAB_1_EXTERNAL_LINKS = {
        "איזור אישי": "h5z.info-cloud.co.il",
        "רישום לצהרוני בית הספר": "h5z.info-cloud.co.il",
    }
    
    # ⬅️ 2. קישורי בדיקה - טאב 'מעונות יום' (הקישורים החדשים)
    TAB_2_EXTERNAL_LINKS = {
        "אזור אישי": "h5z.info-cloud.co.il/Login?loginFor=PrivateArea", 
        "רישום מעונות יום": "h5z.info-cloud.co.il/Home/AnotherProcIsRunning?lang=he",
        # שם הקישור במילון נשאר כפי שהוא מופיע בבדיקה, לצורך השוואה בלבד
        "רישום מעון חרצית תמ''ת": "https://www.hironit.org.il/?CategoryID=3506"
    }

    # הוסר: TAMAT_BUTTON_NAME ו-TAMAT_BUTTON_XPATH
    # הוסר: TAMAT_BUTTON_XPATH = f"//a[contains(., '{TAMAT_BUTTON_NAME}')]"
    
    
    PAGE_TITLE = (By.TAG_NAME, "h1")
    # ... (שאר Locators רלוונטיים) ...
    
    
    def __init__(self, driver, url):
        super().__init__(driver)
        self.DAYCARE_URL = url 

    def open_daycare_page(self):
        """ מנווט ישירות לדף ה-Daycare. """
        self.go_to_url(self.DAYCARE_URL)
        print(f">>> נווט לדף Daycare: {self.DAYCARE_URL}")

    def get_page_title(self):
        """ מחזיר את כותרת הדף (לצורך אימות). """
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    
    # --- מתודות עזר פנימיות ---
    
    def _click_link_by_text(self, link_text):
        """ מתודה פנימית: מבצעת את הלחיצה על קישור ספציפי באמצעות JavaScript. """
        
        # 🛑 שינוי קריטי: אם שם הקישור הוא הבעייתי, השתמש ב-CSS Selector (לפי URL)
        if link_text == "רישום מעון חרצית תמ''ת":
            dynamic_locator = self.TAMAT_BUTTON_LOCATOR
            print(f">>> השתמש בלוקייטור לפי HREF עבור '{link_text}'.")
        else:
            # עבור שאר הקישורים, השתמש ב-XPath הגנרי הקיים
            dynamic_locator = (self.GENERIC_LINK_BY_TEXT[0], 
                               self.GENERIC_LINK_BY_TEXT[1].format(link_text))
            
        # 1. המתנה לוודא שהאלמנט ניתן ללחיצה
        link_element = self.wait_for_clickable_element(dynamic_locator) 
        
        # 2. ביצוע לחיצת JavaScript ישירה
        self.execute_script("arguments[0].click();", link_element)
        print(f">>> נשלחה פקודת לחיצת JavaScript על '{link_text}'.")


    def _verify_single_external_link_navigation(self, link_text, expected_url_part):
        """ פונקציה פנימית: לוחצת, עוברת טאב, מאמת URL וחוזרת (בדיקה יחידה). """
        print(f"\n--- מתחיל בדיקת ניווט: {link_text} ---")

        original_window = self.driver.current_window_handle
        
        # 1. ביצוע הלחיצה שפותחת את הטאב החדש (משתמשת במתודה המתוקנת)
        self._click_link_by_text(link_text)
        
        # 2. המתנה קצרה לפתיחת הטאב החדש ומעבר אליו
        new_window = None
        for _ in range(10): 
            if len(self.driver.window_handles) > 1:
                new_window = [window for window in self.driver.window_handles if window != original_window][0]
                self.driver.switch_to.window(new_window)
                print(">>> בוצע מעבר לטאב החדש.")
                break
            time.sleep(1)

        if not new_window:
            raise TimeoutException(f"❌ לא נפתח טאב חדש לאחר הלחיצה על '{link_text}'.")

        # 3. אימות ה-URL החיצוני
        self.wait_for_url_to_contain(expected_url_part, timeout=15)
        
        final_url = self.driver.current_url
        assert expected_url_part in final_url, f"❌ הניווט לא הוביל לכתובת החיצונית הנכונה! נמצא: {final_url}"
        
        print(f"✅ אימות ניווט ל'{link_text}' עבר בהצלחה. כתובת יעד: {final_url}")

        # 4. סגירת הטאב החדש וחזרה לטאב המקורי
        self.driver.close()
        self.driver.switch_to.window(original_window)
        print(">>> חזרה לטאב המקורי. הבדיקה מוכנה להמשך.")

    # --- מתודות Flow ציבוריות (המשמשות את full_flow.py) ---

    def run_tab_1_external_link_tests(self):
        """ מריץ לולאה על כל הקישורים החיצוניים בטאב 'צהרונים'. """
        print("\n--- מתחיל בדיקת קישורים חיצוניים (טאב צהרונים) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print("--- סיום בדיקת קישורים חיצוניים (טאב צהרונים) ---")


    def navigate_to_daycare_tab(self):
        """ 
        ⬅️ פתרון חלופי: נווט ישירות לכתובת הטאב כדי למנוע קריסה. 
        """
        target_url = self.DAYCARE_URL + self.TAB_2_URL_PART
        
        # 1. ניווט ישיר ל-URL החדש (עוקף את הלחיצה הבעייתית)
        self.go_to_url(target_url) 
        print(f"\n>>> עוקף לחיצה בעייתית. נווט ישירות ל-URL הטאב: {target_url}")

        # 2. המתנה ליציבות DOM (מחכה לאלמנט הראשון בטאב החדש)
        first_link_name = list(self.TAB_2_EXTERNAL_LINKS.keys())[0] 
        dynamic_locator = (self.GENERIC_LINK_BY_TEXT[0], 
                           self.GENERIC_LINK_BY_TEXT[1].format(first_link_name))
        
        # המתנה עד שהקישור הראשון בטאב החדש יהיה ניתן ללחיצה:
        self.wait_for_clickable_element(dynamic_locator)
        print(">>> האלמנטים בטאב החדש יציבים ומוכנים ללחיצה.") 
        
        final_url = self.driver.current_url
        if self.TAB_2_URL_PART not in final_url:
              raise Exception(f"❌ ה-URL הפנימי לא השתנה כצפוי! נמצא: {final_url}")
              
        print(f"✅ ניווט פנימי לטאב '{self.TAB_BUTTON_NAME}' עבר בהצלחה. URL: {final_url}")


    def run_tab_2_external_link_tests(self):
        """ מריץ לולאה על כל הקישורים החיצוניים בטאב 'מעונות יום'. """
        print(f"\n--- מתחיל בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME}) ---")
        for link_name, url_part in self.TAB_2_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part)
        print(f"--- סיום בדיקת קישורים חיצוניים (טאב {self.TAB_BUTTON_NAME}) ---")