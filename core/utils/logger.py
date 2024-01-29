import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Get the current directory and go up one level
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR_PATH = BASE_DIR / "logs"
# Create the logs directory if it doesn't exist
LOG_DIR_PATH.mkdir(parents=True, exist_ok=True)


class LoggerSingleton:
    """
    Singleton class for configuring and managing a logger instance with log rotation.

    This class ensures that the same logger instance is used throughout the project
    while providing log rotation to prevent log files from growing indefinitely.

    Methods:
        setup_logger(log_file_name="bot.log"): Configures the logger with a rotating file handler.
        get_logger(): Retrieves the configured logger instance.

    Args:
        log_file_name (str): The name of the log file. Defaults to "bot.log".
    """

    logger = None  # Class-level attribute for the logger

    def __init__(self, log_file_name="bot.log"):
        """
        Initialize the LoggerSingleton instance.

        Args:
            log_file_name (str): The name of the log file. Defaults to "bot.log".
        """
        self.log_file_name = log_file_name
        self.setup_logger()

    def setup_logger(self):
        """
        Configure the logger with a rotating file handler.
        """

        # Set up logging to file with log rotation
        log_file = LOG_DIR_PATH / self.log_file_name
        log_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        rotating_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=10
        )
        rotating_handler.setFormatter(log_formatter)

        # Set up logging to console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)

        # Create and configure the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(rotating_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """
        Log an info message.
        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def warning(self, message):
        """
        Log a warning message.
        Args:
            message (str): The message to log.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Log an error message.
        Args:
            message (str): The message to log.
        """
        self.logger.error(message)

    @classmethod
    def get_logger(cls):
        """
        Retrieve the configured logger instance.

        Returns:
            logging.Logger: The configured logger instance.
        """
        if cls.logger is None:
            cls.logger = cls()  # Create a new instance if the logger is None
        return cls.logger
