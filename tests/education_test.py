from pathlib import Path
import sys
from sys import path
from selenium import webdriver
import time

# --- Path Fix ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets
from pages.education_page import EducationPage

secrets = load_secrets()

if secrets:
    EDUCATION_URL = secrets.get('education_url')
    user_data = secrets.get('user_data', {})
    STUDENT_ID = user_data.get('id_number')
    STUDENT_PASS = user_data.get('password')
    
    if not STUDENT_ID or not STUDENT_PASS:
        sys.exit(1)

    try:
        print("🚀 Starting Education Interface Test")
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        with driver:
            education_page = EducationPage(driver, EDUCATION_URL)
            education_page.open_education_page()
            
            education_page.verify_education_content()
            education_page.run_default_tab_external_link_tests()

            # 🟢 מיפוי: איזה מילון מתאים לאיזה טאב
            # שמות הטאבים כאן חייבים להיות זהים למה שמופיע ב-side_tabs
            TABS_DATA_MAP = {
                "רישום חינוך יסודי": education_page.TAB_3,
                "רישום חינוך על יסודי": education_page.TAB_4,
                "חינוך מיוחד": education_page.TAB_5,
                "תשלומים": education_page.TAB_6,
                "יצירת קשר": education_page.TAB_7
            }

            side_tabs = [
                "תיק תלמיד",
                "רישום חינוך יסודי",
                "רישום חינוך על יסודי",
                "חינוך מיוחד",
                "תשלומים",
                "יצירת קשר"
            ]
            
            for tab in side_tabs:
                education_page.navigate_to_side_tab(tab)

                # לוגיקה ייחודית לתיק תלמיד
                if tab == "תיק תלמיד":
                    print(f"🛑 Reached '{tab}' - Initiating Login...")
                    success = education_page.perform_student_login(STUDENT_ID, STUDENT_PASS)
                    if not success: raise Exception("Login Failed!")
                    
                    if education_page.navigate_to_online_forms_after_login():
                        education_page.run_online_forms_link_tests()
                    continue # ממשיכים לטאב הבא

                # לוגיקה לשאר הטאבים - שימוש במילונים החדשים
                if tab in TABS_DATA_MAP:
                    # שולפים את המילון המתאים מהמיפוי ושולחים לבדיקה
                    links_dict = TABS_DATA_MAP[tab]
                    education_page.verify_links_from_dictionary(links_dict, tab)
                else:
                    print(f"ℹ️ No links dictionary mapped for tab: {tab}")

            print("\n>>> Education Interface test finished successfully!")
            
    except Exception as e:
        print(f"\n❌ TEST STOPPED: {e}")
        if 'driver' in locals(): time.sleep(5)
        
else:
    print("Cannot proceed without configuration data.")