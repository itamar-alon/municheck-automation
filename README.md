🏙️ Municipal Services Automation
An advanced End-to-End (E2E) test automation framework designed to validate critical digital services for the Rishon LeZion Municipality. The framework simulates real user journeys across multiple modules (Water, Education, Parking, Business Licensing, etc.) to ensure system stability and link integrity.

(Place your Allure dashboard screenshot here)

🚀 Key Features
Page Object Model (POM): Built with a scalable architecture that strictly separates test logic (tests/) from page interaction logic (pages/), ensuring high maintainability.

Performance Optimization (Smart Verify): Implemented a "Smart Link Verification" mechanism. Instead of the slow "Click & Wait" approach, the framework performs static DOM analysis (href validation).

Result: Reduced "Water Interface" test execution time by ~80% (from 6 minutes to ~1 minute).

Robust Error Handling: Automatic screenshot capture upon test failure, saving artifacts with timestamps for debugging.

Advanced Reporting: Full integration with Allure Framework to generate detailed, interactive HTML reports with step-by-step execution logs.

Secure Configuration: Sensitive data (credentials, URLs) is managed via an external secrets.json file, keeping the codebase secure.

🛠️ Tech Stack
Language: Python 3.x

Web Driver: Selenium WebDriver

Test Runner: Pytest

Reporting: Allure Report

IDE: VS Code

📂 Project Structure
Plaintext

├── pages/                  # Page Object Classes
│   ├── base_page.py        # Base class with Selenium wrappers & error handling
│   ├── water_page.py       # Water services logic (Optimized)
│   ├── education_page.py   # Education module logic
│   ├── business_page.py    # Business license logic
│   └── ...
├── tests/                  # Test Scripts (Pytest)
│   ├── test_full_flow.py   # Main E2E execution file
│   └── utils/              # Utilities (Secrets loader, helpers)
├── screenshots/            # Error artifacts (Auto-generated)
├── requirements.txt        # Python dependencies
└── README.md
⚙️ Installation & Setup
1. Clone the Repository
Bash

git clone https://github.com/YourUsername/rishon-automation.git
cd rishon-automation
2. Install Dependencies
Bash

pip install -r requirements.txt
3. Configuration (secrets.json)
Create a secrets.json file in the root directory. This file is ignored by Git to protect sensitive data. Template:

JSON

{
    "water_url": "https://...",
    "education_url": "https://...",
    "business_url": "https://...",
    "daycare_url": "https://...",
    "parking_url": "https://...",
    "enforcement_url": "https://...",
    "street_url": "https://...",
    "user_data": {
        "id_number": "YOUR_ID",
        "password": "YOUR_PASSWORD"
    }
}
🏃‍♂️ How to Run
Execute the Full System Test
Run the comprehensive suite using Pytest:

Bash

python -m pytest tests/test_full_flow.py --alluredir=./allure-results

View the Report
Generate and serve the Allure HTML report:

Bash

%AppData%\npm\allure serve ./allure-results