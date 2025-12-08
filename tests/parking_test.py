from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from pathlib import Path 
import sys 
from sys import path 

# --- 1. Path Fix (Crucial for finding 'pages' directory) ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

# ⬅️ 2. Importing necessary modules
from tests.utils.secrets_loader import load_secrets 
from tests.test_setup import setup_driver_and_login 
from pages.parking_page import ParkingPage # Parking Page Object 


# --- 3. Loading Configuration and Settings ---
secrets = load_secrets()

if secrets:
    user_data = secrets.get('user_data', {})
    PARKING_URL = secrets.get('parking_url')
    
    # ⬅️ Fetch login credentials
    USER_ID = user_data.get('id_number')
    PASSWORD = user_data.get('password')

    # --- 4. Running the Test Flow ---
    try:
        # ⬅️ Step A: Perform Setup and Login
        driver = setup_driver_and_login(secrets)
        
        with driver: # Manages automatic driver closure
            print("✅ Setup and Login successful. Starting Parking Interface test.")
            
            # --- Step B: Initialize and Open Parking Page ---
            parking_page = ParkingPage(driver, PARKING_URL) 
            parking_page.open_parking_page() 
            
            # ⬅️ Title Validation
            page_title = parking_page.get_page_title()
            assert "חניה" in page_title or "Parking" in page_title, "❌ Page title validation failed! Title not related to Parking."
            print(f"✅ Parking page title validation successful: {page_title}") 
            
            
            # --- Step C: Run the Full 3-Tab Flow ---
            
            # 1. Tab 1 (Default): External Links Test
            parking_page.run_tab_1_external_link_tests() 
            
            # 2. Tab 2: Dynamic Data Search Test (כולל Re-authentication)
            parking_page.navigate_to_tab_2()
            # 🟢 קריאה מתוקנת עם העברת פרטי משתמש
            parking_page.search_and_verify_parking_data(USER_ID, PASSWORD) 
            
            # 3. Tab 3: External Links Test
            parking_page.navigate_to_tab_3()
            parking_page.run_tab_3_external_link_tests()
            
            print("\n>>> Parking Interface test finished successfully!") 
            
    except Exception as e:
        print(f"❌ The test failed! Error occurred: {e}")
        
else:
    print("Cannot proceed without login credentials.")