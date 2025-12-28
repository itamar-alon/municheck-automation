from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from pathlib import Path
import sys 
from sys import path 
import time

# --- 1. Path Fix ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

# --- 2. Importing Modules ---
from tests.utils.secrets_loader import load_secrets 
from pages.daycare_page import DaycarePage 
from pages.education_page import EducationPage
from pages.business_page import BusinessLicensePage
from pages.enfo_page import EnforcementPage 
from pages.street_page import StreetPage
from pages.water_page import WaterPage
from pages.parking_page import ParkingPage

# --- 3. Loading Configuration ---
secrets = load_secrets() 

if secrets:
    # שליפת כתובות URL
    DAYCARE_URL = secrets.get('daycare_url')
    EDUCATION_URL = secrets.get('education_url')
    BUSINESS_URL = secrets.get('business_url')
    ENFORCEMENT_URL = secrets.get('enforcement_url')
    STREET_URL = secrets.get('street_url')
    WATER_URL = secrets.get('water_url')
    PARKING_URL = secrets.get('parking_url')

    # שליפת פרטי משתמש
    user_data = secrets.get('user_data', {})
    USER_ID = user_data.get('id_number')
    PASSWORD = user_data.get('password')

    if not USER_ID or not PASSWORD:
        print("❌ Error: Missing credentials in secrets.json")
        sys.exit(1)

    try:
        print("🚀 Starting Full End-to-End Flow Test")
        
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        with driver:
            
            # ==========================================
            # 1. Daycare (צהרונים)
            # ==========================================
            print("\n" + "="*40)
            print("🏗️  Testing Daycare Interface")
            print("="*40)
            
            daycare = DaycarePage(driver, DAYCARE_URL)
            daycare.open_daycare_page()
            
            dc_title = daycare.get_page_title()
            if "צהרונים" in dc_title or "Daycare" in dc_title:
                print(f"✅ Title verified: {dc_title}")
            
            daycare.run_tab_1_external_link_tests()
            daycare.navigate_to_daycare_tab()
            daycare.run_tab_2_external_link_tests()


            # ==========================================
            # 2. Education (חינוך)
            # ==========================================
            print("\n" + "="*40)
            print("🎓 Testing Education Interface")
            print("="*40)

            edu = EducationPage(driver, EDUCATION_URL)
            edu.open_education_page()
            edu.verify_education_content()
            edu.run_default_tab_external_link_tests()

            EDU_TABS_MAP = {
                "רישום חינוך יסודי": edu.TAB_3,
                "רישום חינוך על יסודי": edu.TAB_4,
                "חינוך מיוחד": edu.TAB_5,
                "תשלומים": edu.TAB_6,
                "יצירת קשר": edu.TAB_7
            }

            edu_tabs = [
                "תיק תלמיד",
                "רישום חינוך יסודי",
                "רישום חינוך על יסודי",
                "חינוך מיוחד",
                "תשלומים",
                "יצירת קשר"
            ]

            for tab in edu_tabs:
                edu.navigate_to_side_tab(tab)

                if tab == "תיק תלמיד":
                    print(f"🛑 Reached '{tab}' - Initiating Login...")
                    if edu.perform_student_login(USER_ID, PASSWORD):
                        if edu.navigate_to_online_forms_after_login():
                            edu.run_online_forms_link_tests()
                    else:
                        print("❌ Login failed in Education module.")
                    continue

                if tab in EDU_TABS_MAP:
                    edu.verify_links_from_dictionary(EDU_TABS_MAP[tab], tab)


            # ==========================================
            # 3. Enforcement (פיקוח)
            # ==========================================
            print("\n" + "="*40)
            print("👮 Testing Enforcement Interface")
            print("="*40)

            enfo = EnforcementPage(driver, ENFORCEMENT_URL)
            enfo.open_enforcement_page()
            
            enfo_title = enfo.get_page_title()
            if "פיקוח" in enfo_title: print(f"✅ Title verified: {enfo_title}")
            
            enfo.run_tab_1_external_link_tests()


            # ==========================================
            # 4. Parking (חניה)
            # ==========================================
            print("\n" + "="*40)
            print("🅿️  Testing Parking Interface")
            print("="*40)

            parking = ParkingPage(driver, PARKING_URL)
            parking.open_parking_page()
            
            park_title = parking.get_page_title()
            if "חניה" in park_title: print(f"✅ Title verified: {park_title}")

            parking.run_tab_1_external_link_tests()
            parking.navigate_to_tab_3()
            parking.run_tab_3_external_link_tests()


            # ==========================================
            # 5. Street Info (מידע הנדסי/רחובות)
            # ==========================================
            print("\n" + "="*40)
            print("🛣️  Testing Street Info Interface")
            print("="*40)

            street = StreetPage(driver, STREET_URL)
            street.open_street_page()
            street.search_and_verify_table()
            street.expand_and_verify_popup()


            # ==========================================
            # 6. Water (מים)
            # ==========================================
            if WATER_URL:
                print("\n" + "="*40)
                print("💧 Testing Water Interface")
                print("="*40)
                water = WaterPage(driver, WATER_URL)
                water.open_water_page()
                
                # הרצת טאב 1
                water.run_tab_1_external_link_tests()
                
                # מעבר לטאב 2 והרצה
                water.navigate_to_tab_2()
                water.run_tab_2_external_link_tests()

            # ==========================================
            # 7. Business License (רישוי עסקים)
            # ==========================================
            if BUSINESS_URL:
                print("\n" + "="*40)
                print("💼 Testing Business License Interface")
                print("="*40)
                
                business = BusinessLicensePage(driver, BUSINESS_URL)
                business.open_business_page()
                
                # הרצת בדיקות על כל שלושת הטאבים
                business.run_tab_1_external_link_tests()
                
                business.navigate_to_tab_2()
                business.run_tab_2_external_link_tests()
                
                business.navigate_to_tab_3()
                business.run_tab_3_external_link_tests()

            print("\n" + "="*50)
            print("✅✅✅ FULL END-TO-END FLOW FINISHED SUCCESSFULLY! ✅✅✅")
            print("="*50)

    except Exception as e:
        print(f"\n❌ CRITICAL FAILURE IN FULL FLOW: {e}")
        if 'driver' in locals():
            time.sleep(5)
            
else:
    print("Cannot proceed without configuration data.")