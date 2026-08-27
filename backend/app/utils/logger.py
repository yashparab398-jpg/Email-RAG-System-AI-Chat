import logging
from pathlib import Path

LOG_DIRECTORY = Path("logs")

LOG_DIRECTORY.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIRECTORY / "application.log"
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(
    "enron_email_intelligence"
)