import sys
from pathlib import Path
from selenium import webdriver
import time
from datetime import datetime

# --- Path Setup ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets 
from pages.water_page import WaterPage

# --- Config ---
secrets = load_secrets()
WATER_URL = secrets.get('water_url')
SCREENSHOT_DIR = project_root / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

try:
    print("🚀 Starting Water Interface Test")
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    with driver:
        page = WaterPage(driver, WATER_URL)
        page.open_water_page()
        
        title = page.get_page_title()
        if "מים" in title or "Water" in title:
            print(f"✅ Page Title: {title}")
        else:
             print(f"⚠️ Warning: Title might be different. Got: {title}")
        
        # --- טאב 1 ---
        page.run_tab_1_external_link_tests()
        
        # --- מעבר לטאב 2 וריצה ---
        page.navigate_to_tab_2()
        page.run_tab_2_external_link_tests()
        
        print("\n✅ Water Interface test finished successfully!")

except Exception as e:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_path = str(SCREENSHOT_DIR / f"water_fail_{timestamp}.png")
    
    if 'driver' in locals():
        driver.save_screenshot(screenshot_path)
    
    print(f"\n❌ CRITICAL FAILURE LOGGED")
    print(f"Reason: {e}")
    print(f"📸 Screenshot saved to: {screenshot_path}")
    
    if 'driver' in locals():
        time.sleep(5)
    raise e