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

from core.data import settings

SUPPORT_USERNAME = settings.SUPPORT_USERNAME


menu_structure = {
    "users_main_menu": {
        "text": "☰  به پنل کاربری خوش آمدید. یکی از موارد زیر را انتخاب کنید.",
        "row_width": [1, 2, 1, 1],
        "menu_type": "user",
        "options": [
            {"text": "👤 پروفایل من", "callback_data": "my_profile"},
            {"text": "📦 سرویس های من", "callback_data": "my_services"},
            {"text": "🛍 خرید سرویس", "callback_data": "buy"},
            {"text": "📚 آموزش فعال‌سازی", "callback_data": "how_to's"},
            {"text": "☎️ پشتیبانی", "url": f"{SUPPORT_USERNAME}"},
        ],
    },
    "buy": {
        "text": "یکی از موارد زیر را انتخاب کنید.",
        "back": "users_main_menu",
        "menu_type": "user",
        "options": [
            {"text": "v2Ray | حجمی 🩻", "callback_data": "buy_limited"},
            {"text": "wireguard | نامحدود 🐉", "callback_data": "buy_unlimited"},
        ],
    },
    "how_to's": {
        "text": "سیستم‌عامل متناسب با دستگاه خودتان را انتخاب نمایید.",
        "back": "users_main_menu",
        "menu_type": "user",
        "options": [
            {"text": "🐉 سرویس وایرگارد", "callback_data": "wgGuids"},
            {"text": "🩻 سرویس V2Ray", "callback_data": "v2rayGuids"},
        ],
    },
    "v2rayGuids": {
        "text": "سیستم‌عامل متناسب با دستگاه خودتان را انتخاب نمایید.",
        "row_width": [2, 2, 1],
        "back": "users_main_menu",
        "menu_type": "user",
        "options": [
            {"text": "📱 iOS", "callback_data": "iosGuid"},
            {"text": "📱 Android", "callback_data": "androidGuid"},
            {"text": "💻 macOS", "callback_data": "macGuid"},
            {"text": "💻 Windows", "callback_data": "windowsGuid"},
            {"text": "🐧 Linux", "callback_data": "linuxGuid"},
        ],
    },
    "iosGuid": {
        "text": "نرم افزار دلخواهتان را انتخاب نمایید.",
        "row_width": [1, 1, 1],
        "back": "how_to's",
        "menu_type": "user",
        "options": [
            {"text": "Streisand", "callback_data": "guid_streisandIos_iosGuid"},
            {"text": "V2Box", "callback_data": "guid_V2BoxIos_iosGuid"},
            {"text": "Fair", "callback_data": "guid_Fair_iosGuid"},
        ],
    },
    "macGuid": {
        "text": "نرم افزار دلخواهتان را انتخاب نمایید.",
        "row_width": [1, 1, 1],
        "back": "how_to's",
        "menu_type": "user",
        "options": [
            {"text": "Streisand", "callback_data": "guid_streisandMac_macGuid"},
            {"text": "V2Box", "callback_data": "guid_V2BoxMac_macGuid"},
            {"text": "FoXray", "callback_data": "guid_FoXrayMac_macGuid"},
        ],
    },
    "androidGuid": {
        "text": "نرم افزار دلخواهتان را انتخاب نمایید.",
        "row_width": [1, 1, 1],
        "back": "how_to's",
        "menu_type": "user",
        "options": [
            {"text": "V2rayNG", "callback_data": "guid_V2rayNG_androidGuid"},
        ],
    },
    "windowsGuid": {
        "text": "نرم افزار دلخواهتان را انتخاب نمایید.",
        "row_width": [1, 1, 1],
        "back": "how_to's",
        "menu_type": "user",
        "options": [
            {"text": "win 10+ 64-bit", "callback_data": "win10x64"},
            {"text": "win 7 64-bit", "callback_data": "win7x64"},
            {"text": "win 7 32-bit", "callback_data": "win7x86"},
        ],
    },
    "win10x64": {
        "text": "نرم افزار دلخواهتان را انتخاب نمایید.",
        "row_width": [1, 1, 1],
        "back": "windowsGuid",
        "menu_type": "user",
        "options": [
            {"text": "Nekoray", "callback_data": "guid_NekorayWin10_win10x64"},
        ],
    },
    "win7x64": {
        "text": "نرم افزار دلخواهتان را انتخاب نمایید.",
        "row_width": [1, 1, 1],
        "back": "windowsGuid",
        "menu_type": "user",
        "options": [
            {"text": "Nekoray", "callback_data": "guid_NekorayWin7_win7x64"},
        ],
    },
    "win7x86": {
        "text": "نرم افزار دلخواهتان را انتخاب نمایید.",
        "row_width": [1, 1, 1],
        "back": "windowsGuid",
        "menu_type": "user",
        "options": [
            {"text": "V2rayN", "callback_data": "guid_V2rayN_win7x64"},
        ],
    },
    "linuxGuid": {
        "text": "نرم افزار دلخواهتان را انتخاب نمایید.",
        "row_width": [1, 1, 1],
        "back": "windowsGuid",
        "menu_type": "user",
        "options": [
            {"text": "Nekoray", "callback_data": "guid_NekorayLinux_linuxGuid"},
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
        for _ in range(int(width)):
            if buttons:  # Check if there are still buttons left
                row.append(buttons.pop(0))
        button_rows.append(row)

    markup = InlineKeyboardMarkup()
    for row in button_rows:
        markup.row(*row)

    # Add the Back button if the back key is specified in the menu
    if "back" in menu:
        back_button = InlineKeyboardButton("🔙 بازگشت", callback_data=menu["back"])
        markup.add(back_button)

    # Add the Back to Main Menu button for non-main menus
    # only when the back menu itself has a back button, i.e., we're at least two levels deep
    if "back" in menu and "back" in menu_structure[menu["back"]]:
        main_menu_button = InlineKeyboardButton(
            "🕋 منو اصلی", callback_data="users_main_menu"
        )

        markup.add(main_menu_button)

    return markup, menu_text
