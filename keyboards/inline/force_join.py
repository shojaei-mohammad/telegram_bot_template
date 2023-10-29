from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import config

join_btn = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 عضویت", url=config.CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ عضو شدم", callback_data="joined")],
    ]
)

start_registarion_btn = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=" ✅ شروع کن", callback_data="joined")],
    ]
)


__all__ = ["join_btn", "start_registarion_btn"]
