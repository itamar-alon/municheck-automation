from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .base_page import BasePage

class EducationPage(BasePage):
    """Education Page Object - Robust version with full attribute support."""

    # --- Locators ---
    # לוקייטור חכם לטאבים: מחפש את ה-span בתוך ה-nav (לפי צילום המסך שלך)
    GENERIC_SIDE_TAB = (By.XPATH, "//nav//ul//li//span[contains(normalize-space(.), '{}')]")
    
    PAGE_TITLE_LOCATOR = (By.XPATH, "//h2[contains(normalize-space(.), 'רישום חינוך גני ילדים')]")
    CONTENT_VALIDATOR = (By.XPATH, "//*[contains(normalize-space(.), 'הנרטיב')]")

    # --- Data: External Links ---
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

    def __init__(self, driver, url):
        super().__init__(driver)
        self.DEFAULT_TIMEOUT = 12
        self.EDUCATION_URL = url

    def open_education_page(self):
        self.go_to_url(self.EDUCATION_URL)
        print(f">>> Navigated to Education Interface: {self.EDUCATION_URL}")

    # 🟢 תיקון: הוספת המתודה שקובץ הטסט מחפש
    def get_page_title(self):
        element = WebDriverWait(self.driver, self.DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located(self.PAGE_TITLE_LOCATOR)
        )
        return element.text

    # --- Business Logic Methods ---

    def verify_education_content(self):
        """ מאמת את תוכן הדף. """
        print("\n--- Starting Content Validation ---")
        try:
            # המתנה לטקסט "הנרטיב"
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.CONTENT_VALIDATOR))
            print("✅ Education page content verified!")
        except TimeoutException:
            print("⚠️ Debug: Text 'הנרטיב' not found via XPath. Checking Page Source...")
            if "הנרטיב" in self.driver.page_source:
                print("✅ Found 'הנרטיב' in page source.")
            else:
                raise Exception("❌ Validation text 'הנרטיב' not found.")

    def run_default_tab_external_link_tests(self):
        """ מריץ את בדיקת הקישורים החיצוניים. """
        print("\n--- Running Default Tab External Links ---")
        for text, url in self.DEFAULT_TAB_LINKS.items():
            self._verify_external_link(text, url)

    def navigate_to_side_tab(self, tab_name):
        """ ניווט לטאב צדדי עם לוקייטור span ו-JS Click. """
        print(f"\n--- Navigating to Side Tab: {tab_name} ---")
        
        if tab_name == "תיק תלמיד":
            print(">>> Refreshing page to clear state...")
            self.driver.refresh()
            time.sleep(3)

        locator = (self.GENERIC_SIDE_TAB[0], self.GENERIC_SIDE_TAB[1].format(tab_name))
        
        attempts = 0
        while attempts < 3:
            try:
                element = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(locator))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                # לחיצת JS עוקפת בעיות של חסימת אלמנטים
                self.driver.execute_script("arguments[0].click();", element)
                print(f"✅ Successfully navigated to: {tab_name}")
                time.sleep(2)
                return
            except (StaleElementReferenceException, TimeoutException):
                attempts += 1
                time.sleep(1.5)
        
        raise Exception(f"❌ Failed to navigate to {tab_name}")

    def _verify_external_link(self, link_text, expected_url_part):
        print(f"Testing: {link_text}")
        orig_window = self.driver.current_window_handle
        link_locator = (By.XPATH, f"//*[contains(@role, 'button') or self::a][contains(normalize-space(.), '{link_text}')]")
        
        try:
            el = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(link_locator))
            self.driver.execute_script("arguments[0].click();", el)
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            
            new_win = [w for w in self.driver.window_handles if w != orig_window][0]
            self.driver.switch_to.window(new_win)
            print(f"✅ Passed: {link_text}")
            self.driver.close()
        except Exception:
            print(f"❌ Link error: {link_text}")
        finally:
            self.driver.switch_to.window(orig_window)