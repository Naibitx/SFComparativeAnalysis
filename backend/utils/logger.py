""" Unified logger that writes to both console and a log file. """

import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# one log file per session, named by timestamp
_log_filename = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(_log_filename),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger("sf_comparator")


def log_info(message: str) -> None:
    logger.info(message)


def log_warning(message: str) -> None:
    logger.warning(message)


def log_error(message: str) -> None:
    logger.error(message)


def log_event(event_type: str, assistant: str, task: str, status: str, detail: str = "") -> None:
    # structured log entry for pipeline events such as generation, execution, scan results
    entry = f"[{event_type}] assistant={assistant} task={task} status={status}"
    if detail:
        entry += f" | {detail}"
    logger.info(entry)