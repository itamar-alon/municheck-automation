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

from tests.utils.secrets_loader import load_secrets
from pages.daycare_page import DaycarePage

logger = logging.getLogger("SystemFlowLogger")

def test_daycare_flow(page: Page, secrets):
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    DAYCARE_URL = secrets.get('daycare_url')
    if not DAYCARE_URL:
        logger.error("❌ Error: Missing 'DAYCARE_URL' in .env")
        pytest.fail("Missing 'DAYCARE_URL' in .env")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    try:
        logger.info("🚀 Starting Daycare Test")

        daycare_page = DaycarePage(page, DAYCARE_URL)
        daycare_page.open_daycare_page()

        page_title = daycare_page.get_page_title()
        if "צהרונים" in page_title or "Daycare" in page_title:
             logger.info(f"✅ Page title verified: {page_title}")
        else:
             logger.warning(f"⚠️ Warning: Title might be different. Got: {page_title}")

        daycare_page.run_tab_1_external_link_tests()


        daycare_page.navigate_to_daycare_tab()
        daycare_page.run_tab_2_external_link_tests()

        logger.info("\n>>> Daycare page test completed successfully!")

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