from typing import List, Union, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_keyboard(
    buttons: List[Dict[str, Union[str, None]]]
) -> InlineKeyboardMarkup:
    """
    Creates an InlineKeyboardMarkup with a list of buttons.

    Parameters:
    - buttons: A list of dictionaries, each containing:
        - 'text': The text to display on the button.
        - 'callback_data': The callback data for the button (if applicable).
        - 'url': The URL for the button (if applicable).

    Returns:
    - InlineKeyboardMarkup: An inline keyboard markup object.
    """

    keyboard_list = []
    for btn in buttons:
        if btn.get("callback_data"):
            keyboard_list.append(
                [
                    InlineKeyboardButton(
                        text=btn["text"], callback_data=btn["callback_data"]
                    )
                ]
            )
        elif btn.get("url"):
            keyboard_list.append(
                [InlineKeyboardButton(text=btn["text"], url=btn["url"])]
            )
        else:
            raise ValueError(
                "Either callback_data or url must be provided for each button."
            )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_list)
    return keyboard


__all__ = ["create_inline_keyboard"]
