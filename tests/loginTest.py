from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import json
from pathlib import Path
from .utils.secrets_loader import load_secrets
# ⬅️ Import our Page Object
from pages.login_page import LoginPage

# --- 1. Function to read data (unchanged, correct) ---
def load_secrets(file_name="secrets.json"):
    """Loads configuration data from a JSON file using an absolute path."""

    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    file_path = project_root / file_name

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"*** Attempting to load data from absolute path: {file_path}")
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: File {file_path} is not in a valid JSON format.")
        return None


# --- 2. Loading and configuration ---
secrets = load_secrets()

if secrets:
    # Retrieving login and configuration data
    USER_ID = secrets['user_data']['id_number']
    USER_PASSWORD = secrets['user_data']['password']
    LOGIN_URL = secrets['login_url']
    HOME_URL_PART = secrets['home_url_part']

    # --- 3. Initialize WebDriver and run the test ---

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # The driver.quit() is handled automatically by the 'with' statement
    try:
        with webdriver.Chrome(options=chrome_options) as driver:

            # 1. Initialize the Page Object!
            login_page = LoginPage(driver, LOGIN_URL)

            # 2. 🟢 Fix: Calling the new method for login with password
            login_page.login_with_password(USER_ID, USER_PASSWORD)

            # 3. 🟢 Fix: Waiting for successful navigation (not OTP)
            login_page.wait_for_successful_login(HOME_URL_PART)

            print("✅ Login confirmed. Browser closed automatically.")

    except TimeoutException:
        # ⬅️ Handling Timeout
        print(f"❌ Test failed! Timeout waiting (for URL or element).")
        try:
            current_url = driver.current_url
            print(f"  Current URL is: {current_url}")
        except:
            print(f"  Connection error occurred while attempting to get the URL. Driver is likely closed.")

    except Exception as e:
        # ⬅️ General handling
        print(f"❌ Test failed! An unexpected error occurred: {e}")
        try:
            # Ensure closure in case of an unexpected error
            driver.quit()
        except:
            pass

    print(">>> Script finished.")

else:
    print("Cannot proceed without login data.")