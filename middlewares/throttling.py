from typing import Union

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from utils.logger import LoggerSingleton

# Configure the logger
logger = LoggerSingleton.get_logger()


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for rate limiting of message processing in a Telegram bot.

    Rate limiting, also known as throttling, restricts the number of requests a user can make within a given time frame.
    This middleware provides a mechanism to limit the rate at which users can send messages to the bot.
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix="antiflood_"):
        self.rate_limit = limit
        self.prefix = key_prefix
        super().__init__()
        logger.info(
            "ThrottlingMiddleware initialized with limit: {} and prefix: {}".format(
                limit, key_prefix
            )
        )

    async def on_process_message(self, message: types.Message, _data: dict):
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

        logger.info("Checking rate limit for key: {} with limit: {}".format(key, limit))

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            logger.warning(
                "Throttling triggered for chat_id: {} on key: {}".format(
                    message.from_user.id, key
                )
            )
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def on_pre_process_callback_query(
        self, callback_query: types.CallbackQuery, _data: dict
    ):
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

        logger.info("Checking rate limit for key: {} with limit: {}".format(key, limit))

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            logger.warning(
                "Throttling triggered for chat_id: {} on key: {}".format(
                    callback_query.from_user.id, key
                )
            )
            await self.message_throttled(callback_query, t)
            raise CancelHandler()

    async def on_pre_process_inline_query(self, query: types.InlineQuery, _data: str):
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

        logger.info("Checking rate limit for key: {} with limit: {}".format(key, limit))

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            logger.warning(
                "Throttling triggered for chat_id: {} on key: {}".format(
                    query.from_user.id, key
                )
            )
            await self.message_throttled(query, t)
            raise CancelHandler()

    @staticmethod
    async def message_throttled(
        event: Union[types.Message, types.CallbackQuery, types.InlineQuery],
        throttled: Throttled,
    ):
        """
        Responds to a user if they have exceeded the rate limit.

        This method is called when a user has made too many requests in a short time span.
        It informs the user that they have been throttled.

        Args: event (types.TelegramObject): The incoming event (message, callback query, or inline query) causing the
        throttling. throttled (Throttled): Exception containing details about the rate limiting event.
        """
        if throttled.exceeded_count <= 2:
            if isinstance(event, types.Message):
                await event.reply("Too many requests!")
            elif isinstance(event, types.CallbackQuery):
                await event.message.reply("Too many requests!")
            elif isinstance(event, types.InlineQuery):
                results = [
                    types.InlineQueryResultArticle(
                        id="1",
                        title="Throttled",
                        input_message_content=types.InputTextMessageContent(
                            message_text="Too many requests! Please slow down."
                        ),
                    )
                ]
                await event.answer(results, cache_time=10)
            logger.info(
                "Throttle warning sent to chat_id: {}".format(event.from_user.id)
            )
