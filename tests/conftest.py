import pytest
import sys
import logging
import requests
import time
import os
import platform  
from datetime import datetime
from pathlib import Path

current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tests.utils.secrets_loader import load_secrets 

LOKI_URL = os.environ.get("LOKI_URL", "http://127.0.0.1:3100/loki/api/v1/push")

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

    loki_handler = LokiHandler(url=LOKI_URL, job_name="links_automation")
    loki_handler.setFormatter(formatter)
    logger.addHandler(loki_handler)

logger.propagate = False

def is_running_on_server():
    server_names = ["SERVER-PROD", "NODE-01"] 
    current_node = platform.node()
    return (current_node in server_names or 
            os.environ.get("RUN_ENV") == "server" or 
            os.environ.get("GITHUB_ACTIONS") == "true")

@pytest.fixture(scope="session", autouse=True)
def cleanup_zombies_before_run():
    """ Cleanup any lingering browser processes. """
    if platform.system() == "Windows":
        os.system("taskkill /f /im chrome.exe /t >nul 2>&1")
        os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")
        os.system("taskkill /f /im msedge.exe /t >nul 2>&1")
    else:
        os.system("pkill -f chrome || true")
        os.system("pkill -f chromedriver || true")
        os.system("pkill -f msedge || true")
    
    time.sleep(1)

@pytest.fixture(scope="session")
def secrets():
    data = load_secrets()
    if not data:
        logger.error("❌ Error: Could not load .env")
        pytest.fail("❌ Error: Could not load .env")
    return data
