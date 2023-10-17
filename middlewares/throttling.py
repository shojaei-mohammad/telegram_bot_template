from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware to implement throttling (rate limiting) for message processing.

    Args:
        limit: Number of allowed requests in the time window. Defaults to DEFAULT_RATE_LIMIT.
        key_prefix: Prefix for throttling keys. Defaults to 'antiflood_'.
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix="antiflood_"):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        Process the message before it reaches the handler.
        Implements the rate limiting based on the handler's settings or default settings.

        Args:
            message: Incoming message.
            data: Data related to the message.
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        # Check for custom throttling settings on the handler
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

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        """
        Handle the case where a user has exceeded the rate limit.

        Args:
            message: Incoming message that caused the throttling.
            throttled: Throttling exception with details about the rate limiting.
        """
        if throttled.exceeded_count <= 2:
            await message.reply("Too many requests!")
