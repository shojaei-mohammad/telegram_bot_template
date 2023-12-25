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
