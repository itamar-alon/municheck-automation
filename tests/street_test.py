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

from pages.street_page import StreetPage 

logger = logging.getLogger("SystemFlowLogger")

def test_street_flow(page: Page, secrets):
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    STREET_URL = secrets.get('street_url')
    if not STREET_URL:
        logger.error("❌ Error: Missing 'STREET_URL' in .env")
        pytest.fail("Missing 'STREET_URL' in .env")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    try:
        logger.info("🚀 Starting Street Info Test")

        street_page = StreetPage(page, STREET_URL)
        street_page.open_street_page() 

        logger.info(">>> Waiting for main page elements to load...")

        try:
            # Use the more specific locator from the page object for diagnostic
            street_page.get_element(street_page.STREET_NAME_INPUT_LOCATOR, timeout=10000)
            logger.info("✅ Search component found on page.")
        except Exception:
            if "login" in page.url.lower():
                raise Exception("❌ Redirected to Login page. Authentication might be required to view street info.")
            else:
                raise Exception("❌ Page loaded but Search field is missing. Content might be restricted.")

        logger.info(">>> Starting street search and data verification...")
        street_page.search_and_verify_table() 

        logger.info(">>> Opening popup for extended data verification...")
        street_page.expand_and_verify_popup()

        logger.info("\n>>> Street Info page test finished successfully!") 

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