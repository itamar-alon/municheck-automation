from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, InvalidSelectorException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage
from selenium.webdriver.common.keys import Keys
from .login_page import LoginPage 

class ParkingPage(BasePage):
    """
    Parking Interface Page Object.
    Final version including Paid Reports tab and Media validation.
    """

    # --- Locators ---
    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    TAB_BUTTON_NAME_2 = "חניה - מידע אישי" 
    TAB_BUTTON_NAME_3 = "תווי חניה"
    TAB_2_URL_PART = "?tab=1" 
    TAB_3_URL_PART = "?tab=2"
    TAB_2_CLEAN_LOCATOR = (By.XPATH, "//button[contains(normalize-space(.), 'מידע אישי')]")
    
    TEST_PLATE_NUMBER = "12345678"
    
    # 🟢 לוקייטורים ייחודיים לטאב "דוחות ששולמו"
    PAID_REPORTS_TAB = (By.XPATH, "//button[contains(normalize-space(.), 'דוחות ששולמו / בתהליך משפטי')]")
    
    # 🟢 לוקייטור לאיתור דוח ספציפי בטאב ששולם (משתמשים בדוח הראשון שמופיע שם: 4194705, כפי שנראה ב-image_928e3b.png)
    PAID_REPORT_IDENTIFIER = "4194705"
    PAID_REPORT_VALIDATOR = (By.XPATH, f"//*[contains(normalize-space(.), '{PAID_REPORT_IDENTIFIER}')]")
    
    # 🟢 לוקייטור לתמונת הדוח המורחב
    # מחפש את תגית ה-IMG בתוך אזור 'תמונות:'
    REPORT_IMAGE_LOCATOR = (By.XPATH, "//*[contains(normalize-space(.), 'תמונות:')]//following::img[1]") 

    # אימות לפי מספר רכב
    VEHICLE_NUMBER_VALIDATOR = (By.XPATH, "//*[contains(normalize-space(.), '12345678')]")

    # פעולות הדוח
    PAY_BUTTON_LOCATOR = (By.XPATH, "//button[contains(normalize-space(.), 'לתשלום')]")
    APPEAL_BUTTON_LOCATOR = (By.XPATH, "//button[contains(normalize-space(.), 'להגשת ערעור')]")
    REPORT_ACTION_LINKS = {
        "לתשלום": "https://city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/4?SId=4&LAMASID=283000&digit6=8235&Rechev=12345678",
        "להגשת ערעור": "https://por140.cityforms.co.il/ApplicationBuilder/eFormRender.html?code=812A005056A14F7F11AAA643E0948D54&Process=CitizenAppeal140"
    }

    PRIVACY_GUARD_POPUP = (By.CSS_SELECTOR, ".MuiDialog-container .MuiPaper-root")
    PRIVACY_GUARD_AUTH_BUTTON = (By.XPATH, "//button[contains(text(), 'המשך') or contains(text(), 'כניסה') or contains(text(), 'התחברות')]")
    LOGIN_IFRAME_LOCATOR = (By.XPATH, "//iframe[contains(@src, 'login') or contains(@id,'auth')]")

    # Links Data (נותר לשימוש במתודות הלינקים)
    TAB_1_EXTERNAL_LINKS = {
        "תשלום דו": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/4",
        "הודעת תשלום קנס": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/16",
        "התראה לפני עיקול": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/3",
        "צו עיקול מטלטלין": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/98",
        "שובר דחיית ערעור": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/36"
    }

    TAB_3_EXTERNAL_LINKS = {
        "רשימת אזורי חניה": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/LocalParkingTicketArea.aspx?prm=920082-1&language=he",
        "פירוט חניונים": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/Cityparking.aspx?prm=920082-1&language=he",
        "חידוש תו חניה": "https://mileon-portal.co.il/DynamicForm/resNew.aspx?prm=920082-1&language=he",
        "בדיקת תוקף": "https://mileon-portal.co.il/DynamicForm/ValidationLabelsNew.aspx?prm=920082-1&language=he",
        "השלמת מסמכים": "https://mileon-portal.co.il/DynamicForm/CompletingDocuments.aspx?prm=920082-1&language=he",
        "הקצאת חניה שמורה": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/DisabledParking.aspx"
    }

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.PARKING_URL = url
        self.TAB_1_NAME = "דו''חות חניה - תשלום לפי שובר"
        self.LOGIN_URL = "placeholder_for_login"

    def open_parking_page(self):
        self.go_to_url(self.PARKING_URL)
        print(f">>> Navigated to Parking Interface page: {self.PARKING_URL}")

    def get_page_title(self):
        return self.get_element(self.PAGE_TITLE).text

    # --- Wait and Click Helpers (Omitted for brevity in this response, assumed existing code) ---
    def _wait_for_clickable(self, locator, timeout=None):
        wait_time = timeout if timeout else self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(locator))
    
    def _wait_for_presence(self, locator, timeout=None):
        wait_time = timeout if timeout else self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(locator))

    # --- Click/Navigation Helpers (Full version needed for completeness) ---
    def _get_link_locator(self, link_text):
        return (By.XPATH, f"//a[contains(normalize-space(.), '{link_text}')]")

    def _click_link_by_text(self, link_text, current_links_dict):
        dynamic_xpath_locator = self._get_link_locator(link_text)
        dynamic_css_locator = None
        attempts = 0
        while attempts < 3:
            try:
                locator = dynamic_css_locator if dynamic_css_locator else dynamic_xpath_locator
                element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator))
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
                time.sleep(0.3)
                self.driver.execute_script("arguments[0].click();", element)
                print(f">>> Clicked '{link_text}'")
                return
            except Exception:
                attempts += 1
                if dynamic_css_locator is None and link_text in current_links_dict:
                     dynamic_css_locator = (By.CSS_SELECTOR, f"a[href*='{current_links_dict[link_text]}']")
                time.sleep(0.5)
        raise Exception(f"❌ Failed to click '{link_text}'")

    def _verify_single_external_link_navigation(self, link_text, expected_url_part, links_dict):
        print(f"\n--- Test: {link_text} ---")
        orig = self.driver.current_window_handle
        self._click_link_by_text(link_text, links_dict)
        try:
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            new_win = [w for w in self.driver.window_handles if w != orig][0]
            self.driver.switch_to.window(new_win)
            try: self.wait_for_url_to_contain(expected_url_part, 10)
            except: pass
            if expected_url_part in self.driver.current_url: print(f"✅ Passed: {link_text}")
            else: print(f"❌ Failed URL: {link_text}")
            self.driver.close()
            self.driver.switch_to.window(orig)
        except:
            print("❌ Tab fail")
            self.driver.back()

    def _click_button_and_verify_navigation(self, button_locator, link_text, expected_url_part):
        """Clicks a button (not an 'a' tag) and verifies new window navigation."""
        print(f"\n--- Test: {link_text} ---")
        orig = self.driver.current_window_handle
        
        try:
            button_element = self._wait_for_clickable(button_locator, timeout=10)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button_element)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", button_element)
            print(f">>> Clicked button '{link_text}'")
        except Exception as e:
            raise Exception(f"❌ Failed to click '{link_text}' button: {e}")

        # 2. Verify navigation to a new window/tab
        try:
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            new_win = [w for w in self.driver.window_handles if w != orig][0]
            self.driver.switch_to.window(new_win)
            
            self.wait_for_url_to_contain(expected_url_part, 10) 

            if expected_url_part in self.driver.current_url: 
                print(f"✅ Passed: {link_text}")
            else: 
                print(f"❌ Failed URL: {link_text}")
                
            self.driver.close()
            self.driver.switch_to.window(orig)
            
        except Exception:
            try:
                if expected_url_part in self.driver.current_url:
                    print(f"✅ Passed: {link_text} (Navigated in same window)")
                else:
                    raise Exception("URL mismatch after click.")
            except:
                print(f"❌ Failed: Navigation timeout or wrong URL for {link_text}")
                self.driver.switch_to.window(orig)
                self.driver.back()

    def _switch_tab_safe(self, tab_name, expected_url_part):
        print(f"\n--- Tab: {tab_name} ---")
        locator = self.TAB_2_CLEAN_LOCATOR if tab_name == self.TAB_BUTTON_NAME_2 else (By.XPATH, f"//button[contains(text(), '{tab_name}')]")
        try:
            el = self._wait_for_clickable(locator)
            self.driver.execute_script("arguments[0].click();", el)
        except: pass
        self.handle_re_authentication_prompt()

    def handle_re_authentication_prompt(self):
        try:
            btn = self._wait_for_clickable(self.PRIVACY_GUARD_AUTH_BUTTON, timeout=3)
            self.driver.execute_script("arguments[0].click();", btn)
            return True
        except: return False

    def perform_re_authentication(self, user_id, user_password):
        login_page = LoginPage(self.driver, self.LOGIN_URL)
        iframe = False
        try:
            WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(self.LOGIN_IFRAME_LOCATOR))
            iframe = True
        except: pass
        
        try:
            login_page.login_with_password_inside_modal(user_id, user_password)
            if iframe: self.driver.switch_to.default_content()
            self.wait_for_invisibility(self.PRIVACY_GUARD_POPUP, timeout=10)
            print(">>> Login successful.")
            return True
        except: return False

    def run_tab_1_external_link_tests(self):
        for n, u in self.TAB_1_EXTERNAL_LINKS.items(): self._verify_single_external_link_navigation(n, u, self.TAB_1_EXTERNAL_LINKS)

    def navigate_to_tab_2(self): self._switch_tab_safe(self.TAB_BUTTON_NAME_2, self.TAB_2_URL_PART)
    def navigate_to_tab_3(self): self._switch_tab_safe(self.TAB_BUTTON_NAME_3, self.TAB_3_URL_PART)
    def run_tab_3_external_link_tests(self):
        for n, u in self.TAB_3_EXTERNAL_LINKS.items(): self._verify_single_external_link_navigation(n, u, self.TAB_3_EXTERNAL_LINKS)
        
    def verify_paid_report_media(self):
        """ מבצע מעבר לטאב דוחות ששולמו, הרחבה ואימות תמונת הדוח. """
        print("\n--- Starting Paid Reports Media verification ---")
        
        # 1. מעבר לטאב הפנימי
        try:
            paid_tab_element = self._wait_for_clickable(self.PAID_REPORTS_TAB)
            paid_tab_element.click()
            print(">>> Switched to 'Paid Reports' tab.")
            time.sleep(1)
        except Exception as e:
            raise Exception(f"❌ Failed to switch to Paid Reports tab: {e}")

        # 2. הרחבת הדוח הראשון בטאב (מבוסס על PAID_REPORT_IDENTIFIER)
        try:
            # ה-XPath שנמצא כנכון (מטפס לרכיב האב הלחיץ עם role='button')
            REPORT_ROW_CLICKABLE = (By.XPATH, f"//*[contains(normalize-space(.), '{self.PAID_REPORT_IDENTIFIER}')]//ancestor::div[contains(@role, 'button')]")
            
            report_row_element = self._wait_for_clickable(REPORT_ROW_CLICKABLE, timeout=10)
            report_row_element.click()
            print(f">>> Clicked paid report ({self.PAID_REPORT_IDENTIFIER}) row to expand media details.")
            time.sleep(2) 
        except Exception as e:
            raise Exception(f"❌ Failed to click paid report row: {e}. Report identifier might be incorrect or the element is not clickable.")

        # 3. אימות תמונת המדיה
        try:
            image_element = self._wait_for_presence(self.REPORT_IMAGE_LOCATOR, timeout=7)
            image_src = image_element.get_attribute('src')
            
            if image_src and image_src.startswith('http'):
                print(f"✅ Media verified! Found image with SRC: {image_src[:50]}...")
            else:
                raise Exception("Image element found but SRC attribute is missing or invalid.")
                
        except TimeoutException:
            raise Exception("❌ Failed to verify media: Image element not found after expanding report.")
        
        return True

    def verify_report_actions(self):
        """ מבצע הרחבה של הדוח ובדיקת הקישורים 'לתשלום' ו'להגשת ערעור'. """
        print("\n--- Starting Report Actions verification ---")
        
        # 1. לחיצה על ה-Div/שורה של הדוח כדי להרחיב את הפרטים
        try:
            REPORT_ROW_CLICKABLE = (By.XPATH, f"//*[contains(normalize-space(.), '{self.TEST_PLATE_NUMBER}')]//ancestor::div[contains(@role, 'button')]")
            
            report_row_element = self._wait_for_clickable(REPORT_ROW_CLICKABLE, timeout=10)
            report_row_element.click()
            print(">>> Clicked report row to expand actions.")
            time.sleep(2)
        except Exception as e:
            raise Exception(f"❌ Failed to click report row: {e}. Cannot expand report details.")

        # 2. אימות כפתורים/קישורים באמצעות המתודה החדשה ל-BUTTONS
        self._click_button_and_verify_navigation(
            self.PAY_BUTTON_LOCATOR, 
            "לתשלום", 
            self.REPORT_ACTION_LINKS["לתשלום"]
        )

        self._click_button_and_verify_navigation(
            self.APPEAL_BUTTON_LOCATOR, 
            "להגשת ערעור", 
            self.REPORT_ACTION_LINKS["להגשת ערעור"]
        )

        return True

    def search_and_verify_parking_data(self, user_id, user_password):
        """ מבצע אימות לוגין, מוודא שהנתונים נטענו אוטומטית, וממשיך לבדיקות הדוחות ששולמו. """
        print("\n--- Starting parking data search test ---")
        self.perform_re_authentication(user_id, user_password)

        print(">>> Waiting for page stabilization...")
        time.sleep(3) 

        # 1. בדיקה מקדימה - דוחות שטרם שולמו
        try:
            print(">>> Checking if 'Unpaid Reports' data loaded automatically...")
            element_found = self._wait_for_presence(self.VEHICLE_NUMBER_VALIDATOR, timeout=5)
            print(f"✅ Data Auto-Loaded! Found vehicle number: {element_found.text[:50]}...")
            self.verify_report_actions() # ממשיכים לפעולות דוח שטרם שולם
        except TimeoutException:
            raise Exception("❌ Validation failed. Unpaid Reports data was not auto-loaded after login.")
            
        # 2. הרצת בדיקות הדוחות ששולמו (הטאב הפנימי החדש)
        self.verify_paid_report_media()
        
        return True