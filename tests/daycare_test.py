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
from pages.daycare_page import DaycarePage

# --- Loading Configuration ---
secrets = load_secrets()

if secrets:
    # שליפת כתובת ה-Daycare
    DAYCARE_URL = secrets.get('daycare_url')
    
    if not DAYCARE_URL:
        print("❌ Error: Missing 'daycare_url' in secrets.json")
        sys.exit(1)

    try:
        print("Starting Daycare Interface Test")
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        with driver:
            # --- Step A: Setup Daycare Page ---
            daycare_page = DaycarePage(driver, DAYCARE_URL)
            daycare_page.open_daycare_page()
            
            # --- Step B: Title Validation ---
            page_title = daycare_page.get_page_title()
            if "צהרונים" in page_title or "Daycare" in page_title:
                 print(f"✅ Page title verified: {page_title}")
            else:
                 print(f"⚠️ Warning: Title might be different. Got: {page_title}")
            
            # --- Step C: Run Link Tests (Tab 1 - צהרונים) ---
            daycare_page.run_tab_1_external_link_tests()
            
            # --- Step D: Run Link Tests (Tab 2 - מעונות יום) ---
            # מבצעים ניווט לטאב השני
            daycare_page.navigate_to_daycare_tab()
            # מריצים את בדיקת הקישורים של הטאב השני
            daycare_page.run_tab_2_external_link_tests()

            print("\n>>> Daycare page test completed successfully!")
            
    except Exception as e:
        print(f"\n❌ TEST STOPPED: {e}")
        # אם יש שגיאה כללית בטסט, נשאיר חלון פתוח לקצת זמן
        if 'driver' in locals():
             time.sleep(5)
else:
    print("Cannot proceed without configuration data.")