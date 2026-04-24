import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

def log_info(message: str):
    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def log_error(message: str):
    logger.error(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {message}")

def log_event(event: str, details: dict = None):
    msg = f"[{datetime.now().strftime('%H:%M:%S')}] EVENT: {event}"
    if details:
        msg += f" | {details}"
    logger.info(msg)
