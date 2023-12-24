"""
app.py
======

This module serves as the entry point for the Telegram bot. It initializes the essential components and starts the bot's
polling mechanism. The following steps are taken during the bot's startup:
1. Initializes the database connection.
2. Sets default bot commands.
3. Sends a startup notification to admins.
4. Initializes all message/command handlers.

Furthermore, during shutdown, it sends a shutdown notification to the admins.

Usage:
------
Run this script directly to start the bot:
$ python app.py
"""

from aiogram import executor

from database.redis_tools import initialize_redis, close_redis
from handlers import initialize_handlers
from loader import dp, db_utils, config
from middlewares import throttling, is_joined_channel
from utils.notify_admins import start_up_notification, shut_down_notification
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    """
    Asynchronous function that is executed when the bot starts up.

    :param dispatcher: The dispatcher instance for the bot.
    """

    # Initialize Redis database connection.
    await initialize_redis()

    # Initialize MySQL database connection.
    await db_utils.initialize_database()

    # Set the default commands for the bot.
    await set_default_commands(dispatcher)

    # Send a notification to the admins about bot's startup.
    await start_up_notification(dispatcher)

    # Initialize all the message and command handlers.
    initialize_handlers()


async def on_shutdown(dispatcher):
    """
    Asynchronous function that is executed when the bot shuts down.

    :param dispatcher: The dispatcher instance for the bot.
    """

    # close Redis connection
    await close_redis()

    # Send a notification to the admins about bot's shutdown.
    await shut_down_notification(dispatcher)


# Setting up the middleware for request throttling. This prevents users from
# spamming the bot with too many requests in a short time span.
dp.middleware.setup(throttling.ThrottlingMiddleware())

# setting up middleware to see if the user is joind the channel or not
# If the value of "FORCE_CHANNLE_JOIN" in the .env set to yes it forces the user


print("BOT is running ...")

if __name__ == "__main__":
    # Start the bot's polling mechanism. This method continuously checks
    # for new updates and dispatches them to the appropriate handlers.
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
    )
