import logging
from pathlib import Path

# get the current dir and gor up one level
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR_PATH = BASE_DIR / "logs"
# Create the logs directory if it doesn't exist
LOG_DIR_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR_PATH / "bot.log"


def configure_logger(file_name: str) -> logging.Logger:
    """
    Configures and returns a logger instance for the project.

    Parameters:
    - log_file (str): Path to the file where logs will be saved. Default is "project_log.log".

    Returns:
    - logging.Logger: Configured logger instance for the project.
    """
    # Set up logging to file
    log_file = LOG_DIR_PATH / file_name
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),  # This will allow logging to console as well
        ],
    )

    return logging.getLogger(__name__)
