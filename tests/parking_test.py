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
from pages.parking_page import ParkingPage

# --- Loading Configuration ---
secrets = load_secrets()

if secrets:
    PARKING_URL = secrets.get('parking_url')
    
    if not PARKING_URL:
        print("❌ Error: Missing 'parking_url' in secrets.json")
        sys.exit(1)

    try:
        print("Starting Parking Interface Test")
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        with driver:
            # 1. פתיחת הדף
            parking_page = ParkingPage(driver, PARKING_URL)
            parking_page.open_parking_page()
            
            # 2. בדיקת כותרת
            page_title = parking_page.get_page_title()
            if "חניה" in page_title or "Parking" in page_title:
                 print(f"✅ Page title verified: {page_title}")
            else:
                 print(f"⚠️ Warning: Title might be different. Got: {page_title}")
            
            # 3. בדיקת קישורים - טאב 1 (דוחות חניה)
            parking_page.run_tab_1_external_link_tests()
            
            # 4. מעבר לטאב 3 (דילוג על טאב 2 כפי שביקשת)
            parking_page.navigate_to_tab_3()
            
            # 5. בדיקת קישורים - טאב 3 (תווי חניה)
            parking_page.run_tab_3_external_link_tests()

            print("\n>>> Parking Interface test finished successfully!")
            
    except Exception as e:
        print(f"\n❌ TEST STOPPED: {e}")
        if 'driver' in locals():
             time.sleep(5)
else:
    print("Cannot proceed without configuration data.")