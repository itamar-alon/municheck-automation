import sys
import os
from pathlib import Path
from selenium import webdriver
from datetime import datetime

# --- 1. Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets 
from pages.business_page import BusinessLicensePage 

# --- 2. Configuration ---
secrets = load_secrets()
if not secrets:
    print("❌ Error loading secrets.")
    sys.exit(1)

# יצירת תיקיית צילומי מסך אם אינה קיימת
SCREENSHOT_DIR = project_root / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

# --- 3. Start Test ---
driver = webdriver.Chrome()
driver.maximize_window()

try:
    print(" Starting Business License Test")
    page = BusinessLicensePage(driver, secrets['business_url'])
    page.open_business_page()
    
    # Validation
    title = page.get_page_title()
    print(f"✅ Page Title: {title}")
    
    # שלב א': טאב 1
    # ה-assert בודק אם הפונקציה החזירה True. אם לא - הוא זורק שגיאה ל-except.
    assert page.run_tab_1_external_link_tests(), "Tab 1 has broken or missing links"
    
    # שלב ב': טאב 2
    page.navigate_to_tab_2()
    assert page.run_tab_2_external_link_tests(), "Tab 2 has broken or missing links"
    
    # שלב ג': טאב 3
    page.navigate_to_tab_3()
    assert page.run_tab_3_external_link_tests(), "Tab 3 has broken or missing links"
    
    print("\n>>> ✅ All steps finished successfully!")

except Exception as e:
    # יצירת שם קובץ ייחודי עם תאריך ושעה
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_name = f"failure_{timestamp}.png"
    screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
    
    # צילום המסך יתבצע כאן כי ה-assert זרק AssertionError
    driver.save_screenshot(screenshot_path)
    
    print(f"\n❌ TEST FAILED!")
    print(f"Reason: {e}")
    print(f"📸 Screenshot saved to: {screenshot_path}")
    
    # זריקת השגיאה הלאה כדי שהטרמינל יראה שהסקריפט נכשל
    raise e

finally:
    print("\n--- Closing browser ---")
    driver.quit()