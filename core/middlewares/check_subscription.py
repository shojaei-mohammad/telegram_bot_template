from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.data import settings
from core.utils.bot_tools import edit_or_send_new
from core.utils.logger import LoggerSingleton
from loader import bot

# Configure the logger
logger = LoggerSingleton.get_logger()


class CheckUserSubscription(BaseMiddleware):
    @staticmethod
    async def check_subscription(user: types.User) -> bool:
        chat_id = user.id
        logger.info(f"Checking subscription status for chat_id: {chat_id}")

        chat_member = await bot.get_chat_member(
            chat_id=settings.CHANNEL_ID, user_id=chat_id
        )
        is_subscribed = chat_member.status in ["member", "creator", "administrator"]

        if not is_subscribed:
            # User is not subscribed, send a message with a button to the channel
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            "🔗 عضویت در کانال", url=settings.CHANNEL_LINK
                        )
                    ],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="users_main_menu")],
                ]
            )
            prompt_text = (
                "🌟 متوجه شدیم که هنوز به کانال ما ملحق نشده‌اید. برای استفاده از بخش 'کسب درآمد'، اول نیاز "
                "است که عضو کانال شوید. لطفاً با کلیک روی دکمه زیر به ما بپیوندید. منتظر شما هستیم! 🚀"
            )
            await edit_or_send_new(
                chat_id=chat_id,
                new_text=prompt_text,
                reply_markup=keyboard,
            )

            raise CancelHandler()
        return True

    async def on_pre_process_callback_query(
        self, callback_query: types.CallbackQuery, _data: dict
    ):
        callback_data = callback_query.data
        if callback_data == "my_profile":
            is_subscribed = await self.check_subscription(callback_query.from_user)
            if not is_subscribed:
                # If the user is not subscribed, stop further processing of the callback
                return True
            # If subscribed, continue with normal processing
