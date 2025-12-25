from selenium import webdriver

from selenium.common.exceptions import TimeoutException, WebDriverException

from pathlib import Path

from sys import path



# --- 1. Imports and Path Setup ---

from .utils.secrets_loader import load_secrets

# setup_driver_and_login import removed as it is no longer needed

from pages.daycare_page import DaycarePage





# --- 2. Loading and Configuration ---

secrets = load_secrets()



if secrets:

    # Extract necessary URL

    DAYCARE_URL = secrets['daycare_url']

   

    # --- 3. Running the Test ---

    try:

        # Direct driver initialization without login

        driver = webdriver.Chrome()

        driver.maximize_window()

       

        with driver: # Automatic driver cleanup

            print("✅ Driver initialized successfully. Navigating to Daycare page.")

           

            # --- Step A: Setup Daycare Page ---

            daycare_page = DaycarePage(driver, DAYCARE_URL)

            daycare_page.open_daycare_page()

           

            # --- Step B: Title Validation ---

            page_title = daycare_page.get_page_title()

            assert "צהרונים" in page_title or "Daycare" in page_title, f"❌ Incorrect page title! Received: {page_title}"

            print(f"✅ Daycare page title validation passed: {page_title}")

           

            # --- Step C: Run Link Tests ---

            print(">>> Starting external link tests for Daycare page...")

            daycare_page.run_tab_1_external_link_tests()

           

            print("\n>>> Daycare page test completed successfully!")

           

    except Exception as e:

        print(f"❌ Test failed! An error occurred: {e}")

       

else:

    print("Error: Could not load secrets data (URL).")