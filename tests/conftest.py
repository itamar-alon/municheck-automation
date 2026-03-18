import pytest
import sys
import logging
import requests
import time
import os
import platform # הוספתי לזיהוי מערכת ההפעלה/שם המחשב
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- Path Fix ---
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets 

# --- Custom Loki Handler ---
class LokiHandler(logging.Handler):
    def __init__(self, url, job_name):
        super().__init__()
        self.url = url
        self.job_name = job_name

    def emit(self, record):
        try:
            ts = str(int(time.time() * 1e9))
            log_msg = self.format(record)
            payload = {
                "streams": [{
                    "stream": {"job": self.job_name, "level": record.levelname.lower()},
                    "values": [[ts, log_msg]]
                }]
            }
            requests.post(self.url, json=payload, timeout=2)
        except Exception:
            pass

# --- Logging Setup ---
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_filename = log_dir / f"test_run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

logger = logging.getLogger("SystemFlowLogger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    loki_handler = LokiHandler(url="http://10.77.72.45:3100/loki/api/v1/push", job_name="links_automation")
    loki_handler.setFormatter(formatter)
    logger.addHandler(loki_handler)

logger.propagate = False

# --- בדיקת סביבה (שרת מול מקומי) ---
def is_running_on_server():
    """ 
    פונקציה שבודקת האם אנחנו על השרת. 
    אפשר לבדוק לפי שם המחשב או לפי משתנה סביבה.
    """
    # שנה את ה-hostname לשם של השרת שלך או בדוק אם קיים משתנה סביבה ייחודי לשרת
    server_names = ["SERVER-PROD", "NODE-01"] # רשימת שמות השרתים שלך
    current_node = platform.node()
    return current_node in server_names or os.environ.get("RUN_ENV") == "server"

# --- ניקוי תהליכים חכם ---
@pytest.fixture(scope="session", autouse=True)
def cleanup_zombies_before_run():
    """ מנקה שאריות תהליכים בצורה בטוחה לפני תחילת הריצה """
    if is_running_on_server():
        logger.info("🧹 Server detected: Cleaning up all Chrome and Driver processes...")
        os.system("taskkill /f /im chrome.exe /t >nul 2>&1")
        os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")
    else:
        logger.info("💻 Local PC detected: Cleaning only chromedriver to avoid closing personal tabs...")
        # במחשב אישי סוגרים רק את הדרייבר, זה בדרך כלל מספיק ולא פוגע בכרום האישי
        os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")
    
    time.sleep(1)

# --- Fixtures Global ---
@pytest.fixture(scope="session")
def secrets():
    data = load_secrets()
    if not data:
        logger.error("❌ Error: Could not load secrets.json")
        pytest.fail("❌ Error: Could not load secrets.json")
    return data

@pytest.fixture(scope="function")
def driver():
    logger.info("🌐 Initializing Chrome WebDriver...")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-certificate-errors")
    
    # בשרת מומלץ להריץ ב-Headless כדי למנוע קפיצות של חלונות
    if is_running_on_server():
        chrome_options.add_argument("--headless=new")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        driver.broken_links_list = [] 
        
        yield driver
        
    finally:
        logger.info("🛑 Closing Chrome WebDriver...")
        if 'driver' in locals():
            try:
                driver.quit()
            except Exception as quit_error:
                logger.warning(f"⚠️ Failed to close driver: {quit_error}")