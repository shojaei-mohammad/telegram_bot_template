import datetime

import jdatetime

from utils.logger import LoggerSingleton

# Configure the logger
logger = LoggerSingleton.get_logger()


def convert_english_digits_to_farsi(input_string: str) -> str:
    """
    Convert English digits in a string to their Farsi equivalents.

    Parameters:
    - input_string (str): A string that potentially contains English digits.

    Returns:
    - str: The input string with English digits replaced by their Farsi equivalents.

    Note:
    If an error occurs during the conversion, a log entry is made and the original string is returned.
    """

    farsi_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"

    try:
        digit_translation = str.maketrans(english_digits, farsi_digits)
        return input_string.translate(digit_translation)
    except Exception as e:
        logger.info(f"Error converting to Farsi: {e}")
        return input_string


def convert_to_shamsi(greg_date: datetime) -> str:
    """
    Convert a Gregorian datetime object to Shamsi (Jalali) date.

    Args:
        greg_date (datetime): The datetime object representing a Gregorian date.

    Returns:
        str: Shamsi date in the format "YYYY/MM/DD" or "YYYY/MM/DD HH:MM",
             with digits converted to Farsi. Time is included only if present in the input.

    Raises:
        ValueError: If there's an error related to the datetime object.
    """
    try:
        # Convert Gregorian date to Shamsi date
        shamsi_date = jdatetime.datetime.fromgregorian(datetime=greg_date)
        # Format the Shamsi date with or without time based on input
        if isinstance(greg_date, datetime.date):
            shamsi_date_str = shamsi_date.strftime("%Y/%-m/%-d")
        else:
            shamsi_date_str = shamsi_date.strftime("%Y/%-m/%-d %H:%M")

    except ValueError as e:
        logger.error(
            "An error occurred during the conversion to Shamsi, Error: {0}".format(e)
        )
        return "Invalid Date"

    return convert_english_digits_to_farsi(shamsi_date_str)


def convert_days_to_epoch(expire_days):
    """
    Converts a number of days from the current date-time to its corresponding Unix timestamp (Epoch time).

    Parameters:
    - expire_days (int): The number of days from the current date-time.

    Returns:
    - int: The Unix timestamp (Epoch time) representation of the future date-time.

    Example:
    >>> convert_days_to_epoch(5)
    # Returns the Unix timestamp for 5 days from now.
    """

    # Get the current date-time
    current_dt = datetime.datetime.utcnow()

    # Add the days to get the future date-time
    future_dt = current_dt + datetime.timedelta(days=expire_days)

    # Convert to epoch time in milliseconds
    epoch = int(future_dt.timestamp() * 1000)
    return epoch


def calculate_expiry_epoch_after_first_use(days):
    """
    Calculates the epoch value representing the expiry date set a specific number of days after first use.

    The calculation is based on a predefined relationship where each day corresponds to a fixed negative value.
    This negative value is used as a special code to signify the number of days after first use for expiry.
    The function multiplies the number of days by this fixed negative value to calculate the epoch value.

    Parameters:
    - days (int): The number of days after first use for the expiry.

    Returns:
    - int: The calculated epoch value for the expiry date.

    Example:
    >>> calculate_expiry_epoch_after_first_use(10)
    # Returns -864000000 for an expiry 10 days after first use.
    """

    value_per_day = -86400000
    return value_per_day * days


def convert_epoch_to_days(epoch):
    """
    Converts an epoch timestamp in milliseconds to a human-readable datetime.

    Parameters:
    - epoch_millis (int): Epoch timestamp in milliseconds.

    Returns:
    - datetime: The datetime representation of the epoch timestamp.
    """

    # Convert milliseconds to seconds
    epoch_seconds = epoch / 1000.0

    # Create a datetime object from the seconds
    return datetime.datetime.fromtimestamp(epoch_seconds)


def gb_to_bytes(gb):
    # 1 GB is 1024^3 bytes
    return int(gb * (1024**3))


def bytes_to_gb(byte_value):
    return byte_value / (1024**3)
