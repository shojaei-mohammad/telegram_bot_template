from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import config

SUPPORT_USERNAME = config.SUPPORT_USER_NAME


def button(lang: str) -> InlineKeyboardMarkup:
    # Create an inline keyboard markup with share, support and back buttons.
    referral_menu_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("share", switch_inline_query="ref")],
            [InlineKeyboardButton("support", url=f"{SUPPORT_USERNAME}")],
            [InlineKeyboardButton("main menu", callback_data="users_main_menu")],
        ]
    )
    return referral_menu_markup


__all__ = ["button"]
