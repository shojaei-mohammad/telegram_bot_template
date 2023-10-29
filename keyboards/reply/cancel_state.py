from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


button = ReplyKeyboardMarkup(
    one_time_keyboard=True,
    resize_keyboard=True,
    keyboard=[[KeyboardButton(text="❌ لغو")]],
)


__all__ = ["button"]
