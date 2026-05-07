from pathlib import Path
import sys
from sys import path
import time
from datetime import datetime
import logging
import pytest
from playwright.sync_api import Page

current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

from pages.parking_page import ParkingPage

logger = logging.getLogger("SystemFlowLogger")

def test_parking_flow(page: Page, secrets):
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    PARKING_URL = secrets.get('parking_url')
    if not PARKING_URL:
        logger.error("❌ Error: Missing 'PARKING_URL' in .env")
        pytest.fail("Missing 'PARKING_URL' in .env")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    try:
        logger.info("🚀 Starting Parking Interface Test")

        parking_page = ParkingPage(page, PARKING_URL)
        parking_page.open_parking_page()

        page_title = parking_page.get_page_title()
        if "חניה" in page_title or "Parking" in page_title:
             logger.info(f"✅ Page title verified: {page_title}")
        else:
             logger.warning(f"⚠️ Warning: Title might be different. Got: {page_title}")

        parking_page.run_tab_1_external_link_tests()

        parking_page.navigate_to_tab_3()

        parking_page.run_tab_3_external_link_tests()

        logger.info("\n>>> Parking Interface test finished successfully!")

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"critical_failure_{timestamp}.png"
        screenshot_path = str(SCREENSHOT_DIR / screenshot_name)

        try:
            page.screenshot(path=screenshot_path)
        except:
            pass

        logger.error(f"\n❌ CRITICAL FAILURE LOGGED")
        logger.error(f"Reason: {e}")
        logger.error(f"📸 Screenshot saved to: {screenshot_path}")

        raise e