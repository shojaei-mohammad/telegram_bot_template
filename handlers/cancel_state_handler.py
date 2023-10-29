"""
cancel_state_handler.py - Handle the cancellation of user commands or actions.

This module provides a handler for users wishing to terminate ongoing interactions
with the bot or to exit specific bot dialogues. When the user sends a cancel command,
the bot will terminate any ongoing processes, inform the user of the cancellation,
and provide the user with the main menu for further interactions.

Primary Function:
- `cancel_state`: Detects and processes the user's desire to cancel current interactions.
"""

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from keyboards.inline.main_menu import create_markup
from keyboards.reply import remove_keyboard
from loader import dp
from utils.bot_tools import edit_or_send_new


@dp.message_handler(lambda message: message.text == "❌ لغو", state="*")
async def cancel_state(message: Message, state: FSMContext) -> None:
    """
    Handle the user's request to cancel any ongoing bot interaction.

    This function is triggered when a user sends one of the predefined cancel commands.
    Upon activation, the function will:
    1. Delete the user's cancel command message.
    2. Notify the user of the cancellation.
    3. Finish any ongoing FSM processes.
    4. Display the main menu for further interactions.

    Args:
        message (Message): The message object from the user containing the cancel command.
        state (FSMContext): The current FSM context/state of the user's interaction with the bot.

    Returns:
        None
    """

    # If there's no ongoing FSM process, simply return.
    if state is None:
        return

    # cancellation notification text.
    notification_text = "درخواست شما لغو شد."

    # Delete the user's message with the cancel command.
    await message.delete()

    # Send the notification to the user.
    await edit_or_send_new(
        chat_id=message.chat.id,
        new_text=notification_text,
        reply_markup=remove_keyboard.button,
    )

    # Terminate any ongoing FSM process.
    await state.finish()

    # Generate the main menu markup based on user's language.
    menu, text = await create_markup(menu_key="users_main_menu")

    # Send the main menu to the user.
    await edit_or_send_new(chat_id=message.chat.id, new_text=text, reply_markup=menu)
