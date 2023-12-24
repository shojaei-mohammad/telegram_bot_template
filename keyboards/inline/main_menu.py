"""
main_menu.py
============

Description:
------------
This module defines the structure and utility functions for creating Telegram inline menus.
The primary goal is to simplify the creation of interactive menus for Telegram bots
by providing a predefined menu structure that can be easily customized and extended.
The text content for the menus is also internationalized, enabling support for multiple languages.

Main Components:
---------------
- menu_structure: A dictionary defining the structure and options for each menu.
- create_markup: A utility function that returns a Telegram InlineKeyboardMarkup
  based on a given menu structure and language.

Usage:
------
This module can be imported and utilized in Telegram bot handlers
to display interactive menus to users.

Example:
--------
from main_menu import create_markup

markup, menu_text = await create_markup("users_main_menu", "en")
await message.answer(menu_text, reply_markup=markup)

"""

from typing import Tuple, Optional, Any

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from data.config import CHANNEL_LINK
from loader import config

SUPPORT_USERNAME = config.SUPPORT_USER_NAME
menu_structure = {
    "users_main_menu": {
        "text": "📁 به پنل کاربری خوش آمدید. یکی از موارد زیر را انتخاب کنید.",
        "row_width": [1, 2, 3, 1],
        "menu_type": "user",
        "options": [
            {"text": "🤑کسب درآمد", "callback_data": "my_profile"},
            {"text": "💳 شارژ کیف پول", "callback_data": "user_wallet_recharge"},
            {"text": "🛍 خرید سرویس", "callback_data": "view_plans"},
            {"text": "☎️ پشتیبانی", "callback_data": "support"},
            {"text": "📚 ‌آموزش‌ها", "callback_data": "how_to's"},
            {"text": "📂 سرویس های من", "callback_data": "my_services"},
            {"text": "🤗 عضویت در کانال اطلاع رسانی", "url": f"{CHANNEL_LINK}"},
        ],
    },
    "how_to's": {
        "text": "یکی از موارد زیر را انتخاب کنید:",
        "back": "users_main_menu",
        "menu_type": "user",
        "options": [
            {"text": "📱 نرم افزارها", "callback_data": "softwares_menu"},
            {"text": "📚 راهنما", "callback_data": "guids"},
        ],
    },
}


async def create_markup(menu_key: str) -> Tuple[Any, Optional[str]]:
    """
    Create a Telegram InlineKeyboardMarkup based on a given menu structure.

    The function dynamically constructs an InlineKeyboardMarkup based on predefined structures
    and translates the menu text to the given language.

    Args:
        menu_key (str): The key referencing the desired menu structure.

    Returns:
        Tuple[Any, Optional[str]]: A tuple containing the InlineKeyboardMarkup object and the translated menu text.
                                   Returns (None, None) if the menu_key does not exist.

    Raises:
        It might raise exceptions from the Telegram API library, especially if some arguments like
        callback data or URLs are malformed or if the InlineKeyboardMarkup exceeds the maximum allowed size.
        Proper error handling should be added based on the library's specifics.

    Notes:
        The function uses a global setting from the menu_structure dictionary to create the markup.
        The specific use and visual representation will depend on the Telegram API library and its capabilities.
    """

    # Retrieve the menu based on the key
    menu = menu_structure.get(menu_key)
    # Default row width for menus with 2 or 3 buttons
    default_row_width = [2, 2]

    if not menu:
        return None, None

    options = menu["options"]
    menu_text = menu["text"]
    menu_type = menu.get("menu_type")
    # Use the row_width from menu structure, or default if not present
    row_width = menu.get("row_width", default_row_width)
    # Create markup for the menu options
    buttons = []
    for option in options:
        text = f"{option['text']}"
        if "url" in option:
            item = InlineKeyboardButton(text, url=option["url"])
        elif "web_app" in option:
            item = InlineKeyboardButton(text, web_app=WebAppInfo(url=option["web_app"]))
        else:
            item = InlineKeyboardButton(text, callback_data=option["callback_data"])
        buttons.append(item)

    # Break the buttons into rows based on the row_width list
    button_rows = []
    for width in row_width:
        row = []
        for _ in range(width):
            if buttons:  # Check if there are still buttons left
                row.append(buttons.pop(0))
        button_rows.append(row)

    markup = InlineKeyboardMarkup()
    for row in button_rows:
        markup.row(*row)

    # Add the Back button if the back key is specified in the menu
    if "back" in menu:
        back_button = InlineKeyboardButton("بازگشت", callback_data=menu["back"])
        markup.add(back_button)

    # Add the Back to Main Menu button for non-main menus
    # only when the back menu itself has a back button, i.e., we're at least two levels deep
    if "back" in menu and "back" in menu_structure[menu["back"]]:
        if menu_type == "admin":
            main_menu_button = InlineKeyboardButton(
                "خانه", callback_data="admins_main_menu"
            )
        else:
            main_menu_button = InlineKeyboardButton(
                "🏠 منو اصلی", callback_data="users_main_menu"
            )

        markup.add(main_menu_button)

    return markup, menu_text
