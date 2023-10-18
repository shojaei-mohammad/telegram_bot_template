from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db_utils


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"wellcome {message.from_user.full_name}")
