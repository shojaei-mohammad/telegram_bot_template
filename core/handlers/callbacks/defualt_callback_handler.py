"""
defualt_callback_handler.py - Handle callback queries for the Telegram bot.

This module provides the necessary functions to handle callback queries initiated
by inline keyboard buttons within the bot. It manages user navigation across different
menus and provides feedback based on the user's actions.

The core functionality of this module revolves around the `callback_inline` function,
which dynamically generates or updates the menu shown to the user based on the
callback data received from inline buttons.

Primary Functions:
- `callback_inline`: Asynchronous handler for inline button presses, managing
  the main menu navigation for the bot.

Dependencies:
- aiogram for handling callback queries and interactions with the Telegram Bot API.
- Redis tools for fetching cached user data, particularly their preferred language.
- Inline keyboards to define the structure and layout of the bot's menus.

Note:
This module assumes that all callback data received from inline buttons corresponds
to predefined menus or actions. Unrecognized callback data will trigger a default response.
"""


from aiogram.types import CallbackQuery

from core.keyboards.main_menu import menu_structure, create_markup
from core.utils.logger import LoggerSingleton
from loader import bot, dp

logger = LoggerSingleton.get_logger()


@dp.callback_query_handler(lambda call: True, state=None)
async def callback_inline(call: CallbackQuery):
    """
    Asynchronous handler for callback queries triggered by inline keyboard buttons.

    This function manages the user's navigation in the bot based on the callback data received
    from the inline keyboard buttons. Depending on the callback_data, this function can
    update the current message to reflect a different menu or provide feedback to the user.

    Args:
        call (CallbackQuery): The callback query object containing data about the callback.
    """
    # Extract relevant data from the callback query
    callback_data = call.data
    chat_id = call.message.chat.id

    # Check if the received callback_data matches any menu defined in menu_structure
    if callback_data in menu_structure:
        # Generate the appropriate markup and text for the menu corresponding to callback_data
        markup, menu_text = await create_markup(callback_data)

        # If navigating back to the main menu(s), update the message to reflect this
        if callback_data == "users_main_menu":
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=menu_text,
                reply_markup=markup,
            )

        # If navigating to a submenu or another menu, update the message to reflect that menu
        else:
            if markup:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=menu_text,
                    reply_markup=markup,
                )

    else:
        # If the callback_data doesn't match any known menu, log it and inform the user
        print(callback_data)
        prompt_text = "منو تعریف نشده است."
        await bot.answer_callback_query(call.id, text=prompt_text)
