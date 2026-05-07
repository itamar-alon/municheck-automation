from pathlib import Path
import logging
import pytest
import time
from datetime import datetime
import sys

current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pages.login_page import LoginPage

logger = logging.getLogger("SystemFlowLogger")

def test_login_flow(page, secrets):
    if not secrets:
        logger.error("❌ Error loading secrets.")
        pytest.fail("Error loading secrets.")

    user_data = secrets.get('user_data', {})
    USER_ID = user_data.get('id_number')
    USER_PASSWORD = user_data.get('password')
    LOGIN_URL = secrets.get('login_url')
    HOME_URL_PART = secrets.get('home_url_part')

    if not all([USER_ID, USER_PASSWORD, LOGIN_URL, HOME_URL_PART]):
        logger.error("❌ Error: Missing login configuration in .env")
        pytest.fail("Missing login configuration in .env")

    SCREENSHOT_DIR = project_root / "screenshots"
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    try:
        logger.info("🚀 Starting Login Test")

        login_page = LoginPage(page, LOGIN_URL)

        login_page.login_with_password(USER_ID, USER_PASSWORD)

        login_page.wait_for_successful_login(HOME_URL_PART)

        logger.info("✅ Login confirmed successfully.")

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"login_failure_{timestamp}.png"
        screenshot_path = str(SCREENSHOT_DIR / screenshot_name)

        try:
            page.screenshot(path=screenshot_path)
        except:
            pass

        logger.error(f"\n❌ LOGIN TEST FAILED")
        logger.error(f"Reason: {e}")
        logger.error(f"📸 Screenshot saved to: {screenshot_path}")
        raise e