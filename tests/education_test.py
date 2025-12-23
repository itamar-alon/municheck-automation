from pathlib import Path 
import sys 
from sys import path 

# --- 1. Path Fix ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in path:
    path.append(str(project_root))

# ⬅️ 2. Importing necessary modules
from tests.utils.secrets_loader import load_secrets 
from tests.test_setup import setup_driver_and_login 
from pages.education_page import EducationPage 


# --- 3. Loading Configuration ---
secrets = load_secrets()

if secrets:
    EDUCATION_URL = secrets.get('education_url')
    
    # --- 4. Running the Test Flow ---
    try:
        # Step A: Setup and Login
        driver = setup_driver_and_login(secrets)
        
        with driver:
            print("✅ Setup and Login successful. Starting Education Interface test.")
            
            # Step B: Initialize Education Page
            education_page = EducationPage(driver, EDUCATION_URL) 
            education_page.open_education_page() 
            
            # Step C: Content & Title Validation (Default Tab)
            page_title = education_page.get_page_title()
            assert "חינוך" in page_title, f"❌ Title validation failed! Got: {page_title}"
            print(f"✅ Title verified: {page_title}")
            
            education_page.verify_education_content()

            # Step D: Run Default Tab Links (הקישורים שהגדרת)
            education_page.run_default_tab_external_link_tests()

            # Step E: Side Tabs Navigation Flow
            side_tabs = [
                "תיק תלמיד",
                "רישום חינוך יסודי", 
                "רישום חינוך על יסודי", 
                "חינוך מיוחד", 
                "תשלומים", 
                "יצירת קשר אגף החינוך"
            ]
            
            for tab in side_tabs:
                education_page.navigate_to_side_tab(tab)

            print("\n>>> Education Interface test finished successfully!") 
            
    except Exception as e:
        print(f"❌ The test failed! Error: {e}")
        
else:
    print("Cannot proceed without configuration data.")