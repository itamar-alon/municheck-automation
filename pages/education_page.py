from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import unquote
import os 
from datetime import datetime 
from .base_page import BasePage
from .login_page import LoginPage 

class EducationPage(BasePage):
    """
    Education Page Object.
    Optimized for FAST link checking + Error Screenshots.
    """

    # --- Locators ---
    PAGE_TITLE_LOCATOR = (By.XPATH, "//h2[contains(normalize-space(.), 'רישום חינוך גני ילדים')]")
    CONTENT_VALIDATOR = (By.XPATH, "//*[contains(normalize-space(.), 'הנרטיב')]")
    PRIVACY_GUARD_AUTH_BUTTON = (By.XPATH, "//button[contains(text(), 'המשך') or contains(text(), 'כניסה') or contains(text(), 'התחבר') or contains(text(), 'הזדהות')]")
    PRIVACY_GUARD_POPUP = (By.CSS_SELECTOR, ".MuiDialog-container") 
    LOGIN_IFRAME_TAG = (By.TAG_NAME, "iframe")
    INTERNAL_TAB_ONLINE_FORMS = (By.XPATH, "//*[contains(text(), 'טפסים מקוונים')]")

    # --- Data Dictionaries ---
    
    DEFAULT_TAB_LINKS = {
        "הילדים העירוניים": "https://www.edu-reg.co.il/login?cid=8512834&sys=0&sub=1",
        "והגשת ערעור": "https://www.edu-reg.co.il/closed?cid=8512834&sys=0&sub=2",
        "הגשת ערר": "https://www.edu-reg.co.il/closed?cid=8512834&sys=0&sub=2",
        "ביטול רישום": "https://www.edu-reg.co.il/login?cid=8512834&sys=0&sub=5",
        "נוסח מכתב הרשאה": "rishonlezion.muni.il/Residents/Education/Documents/",
        "על כתובת מגורים": "rishonlezion.muni.il/Residents/Education/Documents/",
        "תצהיר": "rishonlezion.muni.il/Residents/Education/Documents/",
        "הסכמה והתחייבות": "rishonlezion.muni.il/Residents/Education/registrationall/",
        "לגני הילדים": "https://www.edu-reg.co.il/login?cid=8512834&sys=0&sub=5",
        "נספח": "rishonlezion.muni.il/Residents/Education/Documents/",
        "יצירת קשר": "rishonlezion.muni.il/Lists/List21/CustomDispForm"
    }

    ONLINE_FORMS_LINKS = {
        "יפוי כוח": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20ייפוי%20כח%20תשפו%20.pdf", 
        "כתובת מגורים בעיר": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/תצהיר%20מגורים%20תשפו%20%20.pdf",      
        "להורים": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/תצהיר%20הורים%20עצמאיים%20תשפו%20%20.pdf",
        "לימודי חוץ": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20תצהיר%20בקשה%20ללימודי%20חוץ%20תשפו%20.pdf" ,
        "נספח": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/נספח%20ד%20תשפו%20.pdf" ,
        "בגן פרטי": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20בקשה%20להישארות%20שנה%20נוספת%20במעון%20.pdf" ,
        "הסכמה והתחייבות": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20הצהתשפו%20.pdf" ,
        "ויתור סודיות": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20ויתור%20סודיות%20.pdf" ,
        "ביטוח": "https://www.rishonlezion.muni.il/Activities/Pages/CityInsurance.aspx" ,
        "להוראת קבע באשראי": "https://por141.cityforms.co.il/login/ActiveDirectory?returnUrl=%2Fappbuilder%2Fformrender" 
    }

    TAB_3 = {
        "רישום לכיתה": "https://www.edu-reg.co.il/login" ,
        "שיבוץ והגשת וערר": "https://www.edu-reg.co.il/login" ,
        "שיבוץ והגשת ערר": "https://www.edu-reg.co.il/login" ,
        "ביטול רישום לבתי": "https://www.edu-reg.co.il/login" ,
        "נוסח מכתב הרשאה": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20ייפוי%20כח%20תשפו%20.pdf" ,
        "כתב הצהרה": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/תצהיר%20מגורים%20תשפו%20%20.pdf" ,
        "תצהיר ל": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/תצהיר%20הורים%20עצמאיים%20תשפו%20%20.pdf" ,
        "בקשה לאישור לימודי": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20תצהיר%20בקשה%20ללימודי%20חוץ%20תשפו%20.pdf" ,
        "יצירת קשר": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=75" 
    }

    TAB_4 = {
        "תושבים חדשים": "https://www.edu-reg.co.il/login" ,
        "והגשת ערר": "https://www.edu-reg.co.il/login" ,
        "ביטול רישום לבתי": "https://www.edu-reg.co.il/login" ,
        "תצהיר מגורים": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/תצהיר%20מגורים%20תשפו%20%20.pdf" ,
        "ויתור סודיות": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20ויתור%20סודיות%20.pdf" ,
        "תצהיר להורים": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/תצהיר%20הורים%20עצמאיים%20תשפו%20%20.pdf" ,
        "בקשה לאישור": "https://www.rishonlezion.muni.il/Residents/Education/registrationall/Documents/טופס%20תצהיר%20בקשה%20ללימודי%20חוץ%20תשפו%20.pdf" ,
        "יצירת קשר": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=76" 
    }

    TAB_5 = {
        "בתי ספר": "https://www.rishonlezion.muni.il/Residents/Education/SpecialEducation/Pages/Schools.aspx" ,
        "גני ילדים": "https://www.rishonlezion.muni.il/Residents/Education/SpecialEducation/Pages/Kindergardens.aspx" ,
        "ועדת זכאות": "https://www.rishonlezion.muni.il/Residents/Education/SpecialEducation/Pages/Placement.aspx" ,
        "ועדת השגה": "https://www.rishonlezion.muni.il/Residents/Education/SpecialEducation/Pages/appeal.aspx" ,
        "יצירת קשר": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=20" 
    }

    TAB_6 = {
        "תשלומי חינוך": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/29" ,
        "חינוך התראה": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/121" ,
        "תאונות אישיות": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/24" ,
        "בקשה להחזר": "https://tikshuv.rishonlezion.muni.il/hito/#/portal/main" ,
        "בקשת הצטרפות": "https://por141.cityforms.co.il/login/ActiveDirectory?returnUrl=%2Fappbuilder%2Fformrender" 
    }
    
    TAB_7 = {
        "גני": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=22" ,
        "חינוך יסודי": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=75" ,
        "על יסודי": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=76" ,
        "מיוחד": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=20" ,
        "ההסעות": "https://www.rishonlezion.muni.il/Lists/List21/CustomDispForm.aspx?ID=85" 
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 12
        self.EDUCATION_URL = url

    def open_education_page(self):
        self.go_to_url(self.EDUCATION_URL)
        print(f">>> Navigated to Education Interface: {self.EDUCATION_URL}")

    def get_page_title(self):
        element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located(self.PAGE_TITLE_LOCATOR)
        )
        return element.text

    # --- Methods ---

    def verify_education_content(self):
        print("\n--- Starting Content Validation ---")
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.CONTENT_VALIDATOR))
            print("✅ Education page content verified!")
        except TimeoutException:
            raise Exception("❌ Validation text 'הנרטיב' not found.")

    def run_default_tab_external_link_tests(self):
        print("\n--- Running Default Tab External Links ---")
        self.verify_links_from_dictionary(self.DEFAULT_TAB_LINKS, "Default Tab")

    def verify_links_from_dictionary(self, links_dict, context_name="Unknown Tab"):
        print(f"\n--- Running Link Tests for: {context_name} ---")
        if not links_dict:
            print(f"⚠️ Warning: No links defined for {context_name}.")
            return
        for text, url in links_dict.items():
            self._verify_external_link(text, url)

    def navigate_to_side_tab(self, tab_name):
        print(f"\n--- Navigating to Side Tab: {tab_name} ---")
        self.driver.switch_to.default_content()

        if tab_name == "תיק תלמיד":
            self.driver.refresh()
            time.sleep(4) 

        xpath = f"//*[contains(text(), '{tab_name}')]"
        attempts = 0
        while attempts < 3:
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                target_element = None
                for el in elements:
                    if el.is_displayed(): target_element = el; break
                if not target_element and elements: target_element = elements[-1]
                
                if target_element:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_element)
                    time.sleep(0.5)
                    try: target_element.click()
                    except: self.driver.execute_script("arguments[0].click();", target_element)
                    print(f"✅ Successfully navigated to: {tab_name}")
                    time.sleep(2)
                    return
                attempts += 1; time.sleep(1)
            except: attempts += 1; time.sleep(1)
        raise Exception(f"❌ Failed to navigate to {tab_name}")

    def perform_student_login(self, user_id, user_password):
        print(f"\n STARTING LOGIN FLOW via LoginPage")
        try:
            auth_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.PRIVACY_GUARD_AUTH_BUTTON))
            auth_btn.click()
        except: pass
        
        time.sleep(2)
        iframes = self.driver.find_elements(*self.LOGIN_IFRAME_TAG)
        if iframes: self.driver.switch_to.frame(iframes[0])
        
        try:
            login_page = LoginPage(self.driver, self.EDUCATION_URL)
            login_page.login_with_password_inside_modal(user_id, user_password)
        except Exception as e:
            self.driver.switch_to.default_content(); raise e
        
        self.driver.switch_to.default_content()
        try:
            WebDriverWait(self.driver, 15).until(EC.invisibility_of_element_located(self.PRIVACY_GUARD_POPUP))
            print("✅ Login successful! Modal closed.")
            time.sleep(3)
            return True
        except: return False

    def navigate_to_online_forms_after_login(self):
        print("\n--- Navigating to Internal Tab: טפסים מקוונים ---")
        try:
            elements = self.driver.find_elements(*self.INTERNAL_TAB_ONLINE_FORMS)
            visible_tab = None
            for el in elements:
                if el.is_displayed(): visible_tab = el; break
            
            if not visible_tab and elements: visible_tab = elements[-1]
            if not visible_tab: raise Exception("Tab not found")

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", visible_tab)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", visible_tab)
            print("✅ Clicked 'Online Forms' tab.")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Failed to click 'Online Forms' tab: {e}")
            return False

    def run_online_forms_link_tests(self):
        self.verify_links_from_dictionary(self.ONLINE_FORMS_LINKS, "Online Forms Internal")

    # 🟢 פונקציית עזר לצילום מסך בעת שגיאה 🟢
    def _take_error_screenshot(self, link_name):
        try:
            # יצירת תיקיית screenshots אם לא קיימת
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            # יצירת שם קובץ ייחודי עם זמן ושם הלינק
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # מנקים תווים בעייתיים משם הקובץ
            safe_name = "".join([c if c.isalnum() else "_" for c in link_name])
            filename = f"screenshots/error_{safe_name}_{timestamp}.png"
            
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save screenshot: {e}")

    def _verify_external_link(self, link_text, expected_url_part):
        print(f"Testing: {link_text}")
        
        # 1. חיפוש האלמנט
        link_locator = (By.XPATH, f"//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{link_text}')]")
        try:
            el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(link_locator))
        except:
            print(f"❌ Link error: {link_text} (Element not found)")
            self._take_error_screenshot(link_text) # 🟢 צילום מסך בכישלון מציאת כפתור
            return

        # 2. חילוץ URL ישיר (אם אפשר)
        href = el.get_attribute("href")
        
        # 3. אם אין href או שזה כפתור JS - פתיחה מהירה בחלון חדש
        orig_window = self.driver.current_window_handle
        try:
            if href and "http" in href:
                # בדיקה מהירה בלי ללחוץ (אם זה לינק רגיל)
                decoded_href = unquote(href)
                decoded_expected = unquote(expected_url_part)
                if decoded_expected in decoded_href:
                    print(f"✅ Passed: {link_text}")
                    return
            
            # אם צריך ללחוץ
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.2)
            self.driver.execute_script("arguments[0].click();", el)
            
            # המתנה קצרה לחלון חדש
            WebDriverWait(self.driver, 8).until(EC.number_of_windows_to_be(2))
            
            new_win = [w for w in self.driver.window_handles if w != orig_window][0]
            self.driver.switch_to.window(new_win)
            
            # בדיקת URL מהירה
            current_url = unquote(self.driver.current_url)
            expected_decoded = unquote(expected_url_part)

            if expected_decoded in current_url:
                print(f"✅ Passed: {link_text}")
            else:
                 # אזהרה (Warning) לא מצלמת מסך, לפי הדרישה
                 print(f"⚠️ Warning: {link_text} opened but URL differs.\n   Expected: ...{expected_decoded[-20:]}\n   Got:      ...{current_url[-20:]}")
            
            self.driver.close()
        except Exception:
            print(f"❌ Link error: {link_text} (Click failed or window didn't open)")
            self._take_error_screenshot(link_text) # 🟢 צילום מסך בכישלון לחיצה
        finally:
            try: self.driver.switch_to.window(orig_window)
            except: pass