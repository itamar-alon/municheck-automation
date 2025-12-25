import sys
from pathlib import Path
from selenium import webdriver
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
SCREENSHOT_DIR = project_root / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

driver = webdriver.Chrome()
driver.maximize_window()

try:
    print("🚀 Starting Water Interface Test")
    page = WaterPage(driver, secrets['water_url'])
    page.open_water_page()
    
    # Validation
    title = page.get_page_title()
    print(f"✅ Page Title: {title}")
    assert "מים" in title or "Water" in title, f"Unexpected title: {title}"
    
    # טאב 1
    assert page.run_tab_1_tests(), "Tab 1 has broken links"
    
    # טאב 2
    page.navigate_to_tab_2()
    assert page.run_tab_2_tests(), "Tab 2 has broken links"
    
    # טאב 3
    page.navigate_to_tab_3()
    assert page.run_tab_3_tests(), "Tab 3 has broken links"
    
    print("\n>>> ✅ Water Test finished successfully!")

except Exception as e:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_path = str(SCREENSHOT_DIR / f"water_fail_{timestamp}.png")
    driver.save_screenshot(screenshot_path)
    print(f"\n❌ TEST FAILED: {e}")
    print(f"📸 Screenshot saved to: {screenshot_path}")
    raise e

finally:
    driver.quit()