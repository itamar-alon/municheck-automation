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
from pages.enfo_page import EnforcementPage

logger = logging.getLogger("SystemFlowLogger")

def test_enforcement_flow(page: Page, secrets):
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    ENFORCEMENT_URL = secrets.get('enforcement_url')
    if not ENFORCEMENT_URL:
        logger.error("❌ Error: Missing 'ENFORCEMENT_URL' in .env")
        pytest.fail("Missing 'ENFORCEMENT_URL' in .env")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    try:
        logger.info("🚀 Starting Enforcement Interface Test")
        
        enforcement_page = EnforcementPage(page, ENFORCEMENT_URL)
        enforcement_page.open_enforcement_page()
        
        page_title = enforcement_page.get_page_title()
        if "פיקוח" in page_title or "Enforcement" in page_title:
             logger.info(f"✅ Page title verified: {page_title}")
        else:
             logger.warning(f"⚠️ Warning: Title might be different. Got: {page_title}")
        
        enforcement_page.run_tab_1_external_link_tests()

        logger.info("\n>>> Enforcement Interface test finished successfully!")
        
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
