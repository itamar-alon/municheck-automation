from pathlib import Path
import sys
from sys import path
from selenium import webdriver
import time
from datetime import datetime

# --- 1. Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets
from pages.business_page import BusinessLicensePage

# --- 2. Configuration ---
secrets = load_secrets()
if not secrets:
    print("❌ Error loading secrets.")
    sys.exit(1)

BUSINESS_URL = secrets.get('business_url')
if not BUSINESS_URL:
    print("❌ Error: Missing 'business_url' in secrets.json")
    sys.exit(1)

SCREENSHOT_DIR = project_root / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

# --- 3. Start Test ---
try:
    print("🚀 Starting Business License Test")
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    with driver:
        # אתחול ופתיחת דף
        page = BusinessLicensePage(driver, BUSINESS_URL)
        page.open_business_page()
        
        # אימות כותרת
        title = page.get_page_title()
        print(f"✅ Page Title: {title}")
        
        # --- שלב א': טאב 1 (ברירת מחדל) ---
        # הפונקציה מדפיסה תוצאות ומצלמת מסך אם יש שגיאה
        page.run_tab_1_external_link_tests()
        
        # --- שלב ב': טאב 2 ---
        page.navigate_to_tab_2()
        page.run_tab_2_external_link_tests()

        # --- שלב ג': טאב 3 ---
        page.navigate_to_tab_3()
        page.run_tab_3_external_link_tests()

        print("\n>>> Business License test finished successfully!")

except Exception as e:
    # טיפול בשגיאות קריטיות שגרמו לקריסת הטסט (כגון אלמנט לא נמצא בניווט לטאב)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_name = f"critical_failure_{timestamp}.png"
    screenshot_path = str(SCREENSHOT_DIR / screenshot_name)
    
    if 'driver' in locals():
        driver.save_screenshot(screenshot_path)
    
    print(f"\n❌ CRITICAL FAILURE LOGGED")
    print(f"Reason: {e}")
    print(f"📸 Screenshot saved to: {screenshot_path}")
    
    # משאירים דפדפן פתוח לקצת זמן במקרה של שגיאה
    if 'driver' in locals():
        time.sleep(5)
    raise e