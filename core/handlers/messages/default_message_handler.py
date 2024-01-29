from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from core.keyboards.main_menu import create_markup
from core.keyboards.reply import remove_keyboard
from core.utils.bot_tools import edit_or_send_new
from core.utils.logger import LoggerSingleton
from loader import dp, bot, db_utils

logger = LoggerSingleton.get_logger()


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
    chat_id = message.chat.id
    # If there's no ongoing FSM process, simply return.
    if state is None:
        return

    # cancellation notification text.
    notification_text = "درخواست شما لغو شد."

    try:
        # Delete the user's message with the cancel command.
        await message.delete()
    except Exception as err:
        logger.error(f"can not delete the user message!\nError:{err}")

    # Send the notification to the user.
    await bot.send_message(
        chat_id=chat_id,
        text=notification_text,
        reply_markup=remove_keyboard.button,
    )
    await db_utils.reset_last_message_id(chat_id=chat_id)
    # Terminate any ongoing FSM process.
    await state.finish()

    # Generate the main menu markup based on user's language.
    menu, text = await create_markup(menu_key="users_main_menu")

    # Send the main menu to the user.
    await edit_or_send_new(chat_id=chat_id, new_text=text, reply_markup=menu)
