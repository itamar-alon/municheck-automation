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
from pages.business_page import BusinessLicensePage

logger = logging.getLogger("SystemFlowLogger")

def test_business_license_flow(page: Page, secrets):

    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    BUSINESS_URL = secrets.get('business_url')
    if not BUSINESS_URL:
        logger.error("❌ Error: Missing 'BUSINESS_URL' in .env")
        pytest.fail("Missing 'BUSINESS_URL' in .env")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    try:
        logger.info("🚀 Starting Business License Test")


        business_page = BusinessLicensePage(page, BUSINESS_URL)
        business_page.open_business_page()

        title = business_page.get_page_title()
        logger.info(f"✅ Page Title: {title}")


        business_page.run_tab_1_external_link_tests()

        business_page.navigate_to_tab_2()
        business_page.run_tab_2_external_link_tests()

        business_page.navigate_to_tab_3()
        business_page.run_tab_3_external_link_tests()

        logger.info("\n>>> Business License test finished successfully!")

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