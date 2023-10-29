"""
throttling.py
=============

Throttling Middleware for a Telegram bot:

This middleware implements rate limiting (throttling) for a Telegram bot, ensuring users can't flood the bot with
too many messages in a short time span. This is essential for maintaining the performance and security of the bot,
preventing potential abuse. By utilizing the throttling mechanism, the bot can serve many users efficiently and
prevent misuse by over-enthusiastic users or potential attackers.
"""

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for rate limiting of message processing in a Telegram bot.

    Rate limiting, also known as throttling, restricts the number of requests a user can make within a given time frame.
    This middleware provides a mechanism to limit the rate at which users can send messages to the bot.

    Attributes:
        rate_limit (int): Maximum number of allowed requests in the specified time window.
        prefix (str): Prefix used for the key in rate limiting.
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix="antiflood_"):
        """
        Initialize the middleware with the specified rate limit and key prefix.

        Args:
            limit (int, optional): Number of allowed requests in the time window. Defaults to DEFAULT_RATE_LIMIT.
            key_prefix (str, optional): Prefix for rate limiting keys. Defaults to 'antiflood_'.
        """
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, _data: dict):
        """
        Process the message before it reaches its handler.

        This method checks if a user has sent too many messages in a short time span using the bot's handlers'
        specific settings or the default ones.

        Args:
            message (types.Message): The incoming message.
            _data (dict): Data related to the message.
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(
                handler, "throttling_key", f"{self.prefix}_{handler.__name__}"
            )
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    @staticmethod
    async def message_throttled(message: types.Message, throttled: Throttled):
        """
        Responds to a user if they have exceeded the rate limit.

        This method is called when a user has made too many requests in a short time span.
        It informs the user that they have been throttled.

        Args:
            message (types.Message): The incoming message causing the throttling.
            throttled (Throttled): Exception containing details about the rate limiting event.
        """
        if throttled.exceeded_count <= 2:
            await message.reply("Too many requests!")
