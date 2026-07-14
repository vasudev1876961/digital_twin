import logging
import sys
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logger
logger = logging.getLogger("digital_twin")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] - %(message)s"
)

# Stream handler (stdout)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# File handler
file_handler = logging.FileHandler(LOGS_DIR / "app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def get_logger(name: str):
    return logging.getLogger(f"digital_twin.{name}")
