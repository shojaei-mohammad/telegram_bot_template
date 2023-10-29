"""
bot_tools.py - Utility functions for the main Telegram bot.

This module provides essential tools to enhance and simplify tasks for the main bot.
The utilities handle common operations such as:

1. Sending new messages or editing existing ones.
2. Acquiring locks for specific chat IDs to prevent race conditions.

These functions leverage asynchronous programming to efficiently handle multiple
chat operations concurrently, ensuring smoother bot performance.

Dependencies:
- aiogram for bot interactions and error handling.
- Asynchronous database utilities for data retrieval and storage.
- Custom logging for error tracking and debug purposes.
"""

import asyncio

from aiogram.utils.exceptions import (
    MessageToEditNotFound,
    MessageNotModified,
    MessageCantBeEdited,
)

from loader import bot, db_utils

from utils.logger import configure_logger


logger = configure_logger(f"{__name__}.log")
# Dictionary to keep the chat id's lock in memory
chat_id_locks = {}


async def edit_or_send_new(
    chat_id: int,
    new_text: str,
    reply_markup=None,
    parsmode=None,
    disable_web_preview=True,
) -> None:
    """
    Edit a given message in a chat or send a new one if editing is not possible.

    This function first tries to edit an existing message. If editing is not feasible
    due to any reason (e.g., the message is too old, or it was not found),
    it sends a new message.

    Parameters:
    - chat_id (int): ID of the chat where the message should be sent or edited.
    - new_text (str): The content of the message to be sent or edited into.
    - reply_markup (Optional): Additional interface options. Defaults to None.
    - parsmode (Optional): Mode for parsing entities in the message text.
    - disable_web_preview (bool): Disables link previews for links in the message. Defaults to True.

    Note:
    This function performs a check to ensure that any previous bot messages
    in the same chat are deleted before sending or editing the current one.

    Returns:
    - None: The function does not return any value, but it has side effects on the Telegram chat.
    """
    last_msg_id = await db_utils.get_last_bot_message_id(chat_id)
    # Obtain a lock for the given chat_id to ensure synchronous access
    get_lock = await get_chat_id_lock(chat_id)
    async with get_lock:
        if last_msg_id is None:  # Check if we are to send a new message
            last_message = await bot.send_message(
                chat_id=chat_id,
                text=new_text,
                reply_markup=reply_markup,
                parse_mode=parsmode,
                disable_web_page_preview=disable_web_preview,
            )
            message_id = last_message.message_id

            # Store the new message's ID in the database for future reference
            await db_utils.store_message_id(
                chat_id=chat_id, message_id=message_id, is_bot=True
            )
        else:
            try:
                # Try to edit the existing message
                await bot.edit_message_text(
                    text=new_text,
                    chat_id=chat_id,
                    message_id=last_msg_id,
                    reply_markup=reply_markup,
                    parse_mode=parsmode,
                    disable_web_page_preview=disable_web_preview,
                )
            except (
                MessageNotModified,
                MessageToEditNotFound,
                MessageCantBeEdited,
            ) as e:
                # Handle potential errors during the editing process
                logger.error(f"Error while editing message: {e}")

                # If editing failed, send a new message instead
                last_message = await bot.send_message(
                    chat_id=chat_id,
                    text=new_text,
                    reply_markup=reply_markup,
                    parse_mode=parsmode,
                    disable_web_page_preview=disable_web_preview,
                )
                message_id = last_message.message_id

                # Store the new message's ID in the database for future reference
                await db_utils.store_message_id(
                    chat_id=chat_id, message_id=message_id, is_bot=True
                )


async def get_chat_id_lock(chat_id: int) -> asyncio.Lock:
    """
    Retrieve or create an asyncio Lock for a specific chat_id.

    If a lock does not already exist for the provided chat_id, a new lock is
    created and stored in the `chat_id_locks` dictionary. If it exists, the
    existing lock for that chat_id is returned.

    Parameters:
    - chat_id (int): ID of the chat for which the lock is required.

    Returns:
    - asyncio.Lock: The lock associated with the given chat_id.

    Note:
    This function ensures that asynchronous operations related to a specific chat_id
    can be synchronized using the returned lock, thus preventing race conditions.
    """

    # Check if a lock already exists for the chat_id
    # If a lock for chat_id is not in the dictionary, create and store one
    if chat_id not in chat_id_locks:
        chat_id_locks[chat_id] = asyncio.Lock()

    # Return the lock for the chat_id
    return chat_id_locks[chat_id]


def escape_markdown_v2(text: str) -> str:
    # Placeholder sequences
    bold_placeholder = "PLACEHOLDER_FOR_BOLD"
    italic_placeholder = "PLACEHOLDER_FOR_ITALIC"
    mono_placeholder = "PLACEHOLDER_FOR_MONO"

    # Replace valid markdown sequences with placeholders
    text = text.replace("*", bold_placeholder)
    text = text.replace("*", italic_placeholder)
    text = text.replace("*", mono_placeholder)

    # List of special characters that need to be escaped in markdown_v2
    special_chars = [
        "[",
        "]",
        "(",
        ")",
        "~",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]

    # Iteratively escape each special character in the text
    for char in special_chars:
        text = text.replace(char, f"\\{char}")

    # Replace placeholders back to valid markdown sequences
    text = text.replace(bold_placeholder, "*")
    text = text.replace(italic_placeholder, "*")
    text = text.replace(mono_placeholder, "*")

    return text
