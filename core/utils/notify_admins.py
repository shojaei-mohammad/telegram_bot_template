from aiogram import Dispatcher

from core.data.settings import ADMINS
from core.utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


async def start_up_notification(dp: Dispatcher) -> None:
    """
    Notify all admins that the bot has started.

    Args:
        dp (Dispatcher): The Dispatcher instance used to send messages.

    Returns:
        None

    Notes:
        If an error occurs while sending the message to an admin, the error is logged.
    """
    for admin in ADMINS:
        try:
            # Send start-up notification to the admin
            await dp.bot.send_message(admin, "The Bot has been started!")
        except Exception as err:
            # Log any exception that occurs
            logger.error(err)


async def shut_down_notification(dp: Dispatcher) -> None:
    """
    Notify all admins that the bot has been stopped.

    Args:
        dp (Dispatcher): The Dispatcher instance used to send messages.

    Returns:
        None

    Notes:
        If an error occurs while sending the message to an admin, the error is logged.
    """
    for admin in ADMINS:
        try:
            # Send shut-down notification to the admin
            await dp.bot.send_message(admin, "The Bot has been stopped!")
        except Exception as err:
            # Log any exception that occurs
            logger.error(err)
