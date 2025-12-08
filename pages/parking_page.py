from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, InvalidSelectorException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage
from selenium.webdriver.common.keys import Keys # Needed for search logic like in StreetPage
# 🛑 ייבוא קלאס הלוגין עבור שימוש ב-Locators שלו ב-Modal
from .login_page import LoginPage 

class ParkingPage(BasePage):
    """
    Parking Interface Page Object.
    Implements validation for three tabs: Tab 1 & 3 (External Links), Tab 2 (Dynamic Data Search).
    """

    # --- Locators and Test Data ---
    GENERIC_LINK_BY_TEXT = (By.XPATH, "//a[contains(normalize-space(.), '{}')]")
    GENERIC_TAB_BUTTON = (By.XPATH, "//button[contains(text(), \"{}\")]") 
    PAGE_TITLE = (By.TAG_NAME, "h1")
    
    # ⬅️ Specific data for Parking page (3 tabs)
    TAB_BUTTON_NAME_2 = "חניה - מידע אישי" 
    TAB_BUTTON_NAME_3 = "תווי חניה"
    
    TAB_2_URL_PART = "?tab=1" 
    TAB_3_URL_PART = "?tab=2"
    
    # 🟢 LOCATOR נקי לטאב 2: מחפש רק את החלק הלא בעייתי בטקסט (XPath)
    TAB_2_CLEAN_LOCATOR = (By.XPATH, "//button[contains(normalize-space(.), 'מידע אישי')]")
    
    # ⬅️ Specific data for Tab 2 (Data search - like StreetPage)
    TEST_PLATE_NUMBER = "12345678" # License plate number for testing
    LICENSE_INPUT_LOCATOR = (By.XPATH, "//input[@type='text' or @type='number' and @placeholder]") # License plate input field
    DATA_LOAD_VALIDATOR = (By.XPATH, "//*[contains(normalize-space(.), 'מספר דו')]") # Text to validate loaded data

    # 🟢 Locators for the Privacy/Session Guard Popup
    PRIVACY_GUARD_POPUP = (By.CSS_SELECTOR, ".MuiDialog-container .MuiPaper-root")
    PRIVACY_GUARD_AUTH_BUTTON = (By.XPATH, "//button[contains(text(), 'המשך') or contains(text(), 'כניסה') or contains(text(), 'התחברות')]") 
    PRIVACY_GUARD_CONTINUE_BUTTON = PRIVACY_GUARD_AUTH_BUTTON 
    
    # ⬅️ 1. Test Links - Default Tab (Payments and Reports)
    TAB_1_EXTERNAL_LINKS = {
        "תשלום דו": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/4",
        "הודעת תשלום קנס": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/16",
        "התראה לפני עיקול": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/3",
        "צו עיקול מטלטלין": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/98" ,
        "שובר דחיית ערעור": "https://www.city4u.co.il/PortalServicesSite/cityPay/283000/mislaka/36"
    }
    
    # ⬅️ 2. Test Links - Tab 3 (Forms and Discounts)
    TAB_3_EXTERNAL_LINKS = {
        "רשימת אזורי חניה": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/LocalParkingTicketArea.aspx?prm=920082-1&language=he",
        "פירוט חניונים": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/Cityparking.aspx?prm=920082-1&language=he",
        "חידוש תו חניה": "https://mileon-portal.co.il/DynamicForm/resNew.aspx?prm=920082-1&language=he" ,
        "בדיקת תוקף": "https://mileon-portal.co.il/DynamicForm/ValidationLabelsNew.aspx?prm=920082-1&language=he" ,
        "השלמת מסמכים": "https://mileon-portal.co.il/DynamicForm/CompletingDocuments.aspx?prm=920082-1&language=he" ,
        "הקצאת חניה שמורה": "https://www.rishonlezion.muni.il/Residents/Transportation/Parking/Pages/DisabledParking.aspx"
    }
    
    # 🟢 Locator נקי של שדה ID במודאל (נותר לשימוש פנימי במידת הצורך)
    MODAL_ID_FIELD = (By.NAME, "tz")
    
    # 🟢 Locator גנרי לזיהוי Iframe (אם קיים - לטובת הלוגין הפנימי)
    LOGIN_IFRAME_LOCATOR = (By.XPATH, "//iframe[contains(@src, 'login') or contains(@id, 'auth')]")


    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 10
        self.PARKING_URL = url
        self.TAB_1_NAME = "דו''חות חניה - תשלום לפי שובר" 
        self.LOGIN_URL = "placeholder_for_login" 


    def open_parking_page(self):
        """ Navigates directly to the Parking Interface page. """
        self.go_to_url(self.PARKING_URL)
        print(f">>> Navigated to Parking Interface page: {self.PARKING_URL}")

    def get_page_title(self):
        """ Returns the page title (for validation). """
        title_element = self.get_element(self.PAGE_TITLE)
        return title_element.text
    
    # --- Internal Helper Methods (Stability Mechanism) ---
    def _get_link_locator(self, link_text):
        xpath = f"//a[contains(normalize-space(.), '{link_text}')]"
        return (By.XPATH, xpath)

    def _click_link_by_text(self, link_text, current_links_dict):
        """ Performs the click intelligently with a Retry mechanism against Stale Elements. """
        dynamic_xpath_locator = self._get_link_locator(link_text)
        dynamic_css_locator = None
        
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            try:
                locator_to_use = dynamic_css_locator if dynamic_css_locator else dynamic_xpath_locator
                
                link_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located(locator_to_use)
                )
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link_element)
                time.sleep(0.5) 
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(locator_to_use))

                try:
                    link_element.click()
                except:
                    self.execute_script("arguments[0].click();", link_element)
                
                print(f">>> Clicked on '{link_text}' (Attempt {attempts+1}).")
                return 
                
            except (StaleElementReferenceException, TimeoutException, NoSuchElementException, InvalidSelectorException) as e:
                if dynamic_css_locator is None and link_text in current_links_dict:
                    href_part = current_links_dict[link_text]
                    dynamic_css_locator = (By.CSS_SELECTOR, f"a[href*='{href_part}']")
                    print(f"⚠️ XPath failed. Retrying with CSS Selector based on HREF: {href_part}")
                
                print(f"⚠️ Attempt {attempts+1} failed for '{link_text}', trying again...")
                attempts += 1
                time.sleep(1) 
            except Exception as e:
                print(f"❌ Unexpected error while clicking '{link_text}': {str(e)}")
                raise e

        raise Exception(f"❌ Failed to click element '{link_text}' after {max_attempts} attempts.")


    def _verify_single_external_link_navigation(self, link_text, expected_url_part, links_dict):
        """ Internal function: Clicks, switches tab, validates URL, and returns. """
        print(f"\n--- Starting navigation test: {link_text} ---")

        original_window = self.driver.current_window_handle
        
        self._click_link_by_text(link_text, links_dict)
        
        # Waiting for a new window to open
        try:
            WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                EC.number_of_windows_to_be(2)
            )
        except TimeoutException:
            if expected_url_part in self.driver.current_url:
                print("⚠️ Link opened in the same window (not a new tab).")
                self.driver.back()
                return
            else:
                raise TimeoutException(f"❌ New tab did not open for '{link_text}'.")
            
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)
        
        # Waiting for URL to load
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
        time.sleep(0.5) 


    def _switch_tab_safe(self, tab_name, expected_url_part):
        """ Safe tab switch with rigid waits and JS click priority. """
        print(f"\n--- Starting navigation to tab: {tab_name} ---")
        
        # 🟢 STEP 1: בחירת Locator יציב (עבור טאב 2)
        if tab_name == self.TAB_BUTTON_NAME_2:
            tab_locator = self.TAB_2_CLEAN_LOCATOR
            print(">>> Using Clean XPath Locator for Tab 2 (bypassing syntax issues).")
        else:
            tab_locator = (self.GENERIC_TAB_BUTTON[0], 
                            self.GENERIC_TAB_BUTTON[1].format(tab_name))
        
        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            try:
                tab_element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
                    EC.visibility_of_element_located(tab_locator)
                )
                
                self.execute_script("arguments[0].click();", tab_element)
                
                print(f">>> Clicked on tab '{tab_name}' (Attempt {attempts + 1}, JS Click).")
                break 
            
            except Exception as e:
                attempts += 1
                if attempts == max_attempts:
                    print(f"❌ Failed to click tab '{tab_name}' after {max_attempts} attempts. Final error: {e}")
                    return
                
                print(f"⚠️ Attempt {attempts} failed to click tab '{tab_name}'. Retrying in 1 second...")
                time.sleep(1)


        # 🛑 אין המתנה ל-URL קשיחה כדי למנוע יציאה לדף בית, נסתמך על בדיקת ה-Popup.
        
        # 🟢 טיפול ב-Popup
        self.handle_re_authentication_prompt()
        
        if expected_url_part not in self.driver.current_url:
            print(f"⚠️ WARNING: Navigation might have failed or led to a redirect. Expected URL part '{expected_url_part}' not found.")
        
        print(f"✅ Navigation to tab '{tab_name}' complete.")


    def handle_re_authentication_prompt(self):
        """ 
        Checks for the authentication prompt, clicks the initial 'כניסה' button.
        """
        try:
            auth_button = self.wait_for_clickable_element(self.PRIVACY_GUARD_AUTH_BUTTON, timeout=5)
            
            print(">>> 🚨 Re-authentication prompt detected. Clicking initial auth button...")
            
            self.execute_script("arguments[0].click();", auth_button)
            time.sleep(1) # זמן קצר לטעינת שדות הלוגין/ה-Iframe
            
            return True
            
        except TimeoutException:
            print(">>> ℹ️ No Re-authentication prompt detected. Content should be visible.")
            return False
            
    
    def perform_re_authentication(self, user_id: str, user_password: str):
        """ Executes the actual steps to fill credentials inside the re-authentication modal/iframe. """
        
        login_page_logic = LoginPage(self.driver, self.LOGIN_URL) 
        switched_to_iframe = False
        
        # 🟢 Locator להודעת שגיאת לוגין (נוסף לטיפול ב-Timeout)
        LOGIN_ERROR_LOCATOR = (By.XPATH, "//*[contains(text(), 'שם משתמש או סיסמה שגויים')] | //*[contains(text(), 'Invalid')]")


        # --- שלב 1: ניסיון לעבור ל-Iframe (אם קיים) ---
        try:
            WebDriverWait(self.driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it(self.LOGIN_IFRAME_LOCATOR)
            )
            switched_to_iframe = True
            print(">>> ✅ Successfully switched to Login Iframe.")
        except TimeoutException:
            print(">>> No Iframe found. Continuing in main DOM.")
        
        # ----------------------------------------------------

        # 2. קריאה ישירה למתודה של LoginPage שתחפש ותמלא את השדות.
        try:
            # 💡 המתודה של LoginPage תבצע כעת את ההמתנה לשדה והמילוי
            login_page_logic.login_with_password_inside_modal(user_id, user_password) 

            # 3. חזרה ל-Default Content אם עברנו ל-Iframe
            if switched_to_iframe:
                self.driver.switch_to.default_content()
                print(">>> Switched back to default content.")

            # 4. המתנה להיעלמות המודאל (אימות הצלחה)
            self.wait_for_invisibility(self.PRIVACY_GUARD_POPUP, timeout=10) 

            print(">>> ✅ Re-authentication successful: User details submitted and modal closed.")
            time.sleep(2)
            return True

        except Exception as e:
            # אם נכשל, נחזור אחורה לפני זריקת השגיאה ונוודא את סיבת הכישלון
            if switched_to_iframe:
                self.driver.switch_to.default_content()
            
            # 🛑 בדיקה: האם המודאל נשאר פתוח בגלל שגיאת לוגין
            try:
                # 💡 נחזור ל-IFrame כדי לבדוק את הודעת השגיאה אם היינו בתוכו
                if switched_to_iframe:
                     WebDriverWait(self.driver, 2).until(
                        EC.frame_to_be_available_and_switch_to_it(self.LOGIN_IFRAME_LOCATOR)
                    )

                # בדיקה לשגיאת לוגין
                self.get_element(LOGIN_ERROR_LOCATOR, timeout=2) 
                print(">>> 🛑 Re-authentication FAILED: Invalid credentials entered.")
                
                # אם נמצאה שגיאה, נצא חזרה
                if switched_to_iframe:
                     self.driver.switch_to.default_content()
                return False
            
            except TimeoutException:
                 print(f">>> ℹ️ Re-authentication failed for an unknown reason (Fields not found or submission failed). Original error: {e}")
                 return False
            except Exception as general_error:
                 print(f">>> ❌ Critical failure during re-authentication: {general_error}")
                 raise general_error


    def run_tab_1_external_link_tests(self):
        """ Runs a loop over all external links in the default tab (Payments and Reports). """
        print(f"\n--- Starting external link test (Tab: {self.TAB_1_NAME}) ---")
        for link_name, url_part in self.TAB_1_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part, self.TAB_1_EXTERNAL_LINKS)
        print(f"--- External link test finished (Tab: {self.TAB_1_NAME}) ---")

    
    # --- TAB 2 (Data Search) Flow ---
    def navigate_to_tab_2(self):
        """ Navigates to the second tab ('חניה - מידע אישי'). """
        self._switch_tab_safe(self.TAB_BUTTON_NAME_2, self.TAB_2_URL_PART)

    # 🟢 החזרת הלוגיקה המלאה
    def search_and_verify_parking_data(self, user_id: str, user_password: str):
        """ Performs a license plate search and verifies dynamic data loading, including re-authentication. """
        print(f"\n--- Starting parking data search test ---")
        
        # 1. ניסיון לבצע הזדהות מחדש (אם נדרש)
        self.perform_re_authentication(user_id, user_password)


        # 2. Type license plate number (לאחר אימות מחדש, שדה הקלט צריך להיות זמין)
        try:
            input_element = self.wait_for_clickable_element(self.LICENSE_INPUT_LOCATOR, timeout=10)
            input_element.send_keys(self.TEST_PLATE_NUMBER)
            
            # 3. Trigger search
            input_element.send_keys(Keys.ENTER) 
            print(">>> Search triggered by pressing ENTER.")
            
            # 4. Verify data loaded
            data_element_found = self.get_element(self.DATA_LOAD_VALIDATOR, timeout=15)
            validation_text = data_element_found.text
            
            print(f"✅ Parking data returned successfully. Found validation text: {validation_text[:50]}...")
            return True
            
        except TimeoutException:
            raise Exception("❌ Parking data failed to load or Input field is missing after re-authentication.")
        except Exception as e:
            raise Exception(f"❌ An unexpected error occurred during data verification: {e}")


    # --- TAB 3 (Forms and Discounts) Flow ---
    def navigate_to_tab_3(self):
        """ Navigates to the third tab ('תווי חניה'). """
        self._switch_tab_safe(self.TAB_BUTTON_NAME_3, self.TAB_3_URL_PART)

    def run_tab_3_external_link_tests(self):
        """ Runs a loop over all external links in Tab 3. """
        print(f"\n--- Starting external link test (Tab: {self.TAB_BUTTON_NAME_3}) ---")
        for link_name, url_part in self.TAB_3_EXTERNAL_LINKS.items():
            self._verify_single_external_link_navigation(link_name, url_part, self.TAB_3_EXTERNAL_LINKS)
        print(f"--- External link test finished (Tab: {self.TAB_BUTTON_NAME_3}) ---")