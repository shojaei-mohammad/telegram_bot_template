from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

referral_menu_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("🚀 اشتراک گذاری لینک", switch_inline_query="share")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="users_main_menu")],
    ]
)
