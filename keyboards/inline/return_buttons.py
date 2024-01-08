from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def add_return_buttons(
    markup: InlineKeyboardMarkup,
    back_callback: str = None,
    include_main_menu: bool = True,
) -> None:
    """
    Adds common buttons to an existing inline keyboard markup.

    This function appends a 'Back' button and optionally a 'Main Menu' button to the provided inline keyboard markup.
    These buttons facilitate navigation in the bot's interface.

    Args:
        markup (InlineKeyboardMarkup): The existing inline keyboard markup to which the buttons will be added.
        back_callback (str): The callback data associated with the 'Back' button.
        include_main_menu (bool, optional): Determines whether to include the 'Main Menu' button. Default is True.

    Returns:
        None: The function directly modifies the passed InlineKeyboardMarkup object.
    """

    # Add a 'Back' button with the provided callback data
    if back_callback is not None:
        back_button = InlineKeyboardButton("🔙 بازگشت", callback_data=back_callback)
        markup.add(back_button)

    # Optionally add a 'Main Menu' button
    if include_main_menu:
        main_menu_button = InlineKeyboardButton(
            "🏠 منو اصلی", callback_data="users_main_menu"
        )
        markup.add(main_menu_button)
