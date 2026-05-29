import logging
import sys
import time
from pathlib import Path

from app.config import settings
from app.constants import LOG_DIR

def configure_logging():
    """Configure logging for entrypoints"""    
    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)
    
    log_file = LOG_DIR / f"app_{int(time.time())}.log"
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)