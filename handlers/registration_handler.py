"""
registration_handler.py - Manage user registration and language preferences.

This module provides handlers for users interacting with the bot for the first time or
when they're updating their details, like changing the language of interaction.

Primary Handlers:
- `bot_start`: Initiate bot interaction with new users.
- `handle_subscription`: Ensure users have joined the necessary channels.
- `handle_select_lang`: Process and save the language selection of a user.
- `handle_phone_registration`: Register the user's phone number and related details.

Utility Functions:
- `ask_for_language_selection`: Present the language selection menu to users.
- `register_user`: Register user details into the database.
"""

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery

from keyboards.inline.main_menu import create_markup
from loader import dp, bot, db_utils, config
from utils import logger

logger = logger.configure_logger("registration_handler.log")


@dp.message_handler(CommandStart(deep_link=None))
async def bot_start(message: types.Message, state: FSMContext) -> None:
    """
    Begin the interaction with the bot.

    This handler gets activated when a user starts the bot, possibly with a referral link.


    Args:
        message (types.Message): The message object from the user starting the bot.
        state (FSMContext): The current FSM context/state of the user's interaction with the bot.

    Returns:
        None
    """
    chat_id = message.chat.id
    args = message.get_args()
    referrer_id = None
    if args:
        referrer_id = args.split("-")[1]

    await state.set_data({"referrer_id": referrer_id})
    menu, text = await create_markup(menu_key="users_main_menu")
    last_msg = await bot.send_message(text=text, chat_id=chat_id, reply_markup=menu)
    await db_utils.store_message_id(message.chat.id, last_msg.message_id, is_bot=True)


@dp.callback_query_handler(lambda call: call.data == "joined")
async def handle_subscription(call: CallbackQuery) -> None:
    """
    Check if a user has joined the required channel.

    If the user has joined the channel, initiate the registration process.

    Args:
        call (CallbackQuery): The callback object containing the user's interaction details.

    Returns:
        None
    """
    channel_id = config.CHANNEL_ID
    chat_id = call.message.chat.id
    chat_member = await bot.get_chat_member(channel_id, chat_id)
    # Check if the chat id exists in the users table
    query = "SELECT COUNT(*) FROM Users WHERE ChatID=%s"
    user_exists = await db_utils.fetch_data(query, (chat_id,), fetch_one=True)
    if user_exists[0] > 0 and chat_member.status in [
        "member",
        "creator",
        "administrator",
    ]:
        await call.message.delete()
        await bot.answer_callback_query(call.id)
        menu, text = await create_markup(menu_key="users_main_menu")
        await bot.send_message(
            text=text, chat_id=call.message.chat.id, reply_markup=menu
        )

    elif chat_member.status in ["member", "creator", "administrator"]:
        await call.message.delete()
        await bot.answer_callback_query(call.id)
        # handle the action after the user subscribed to channel

    else:
        await call.answer("لطفادر کانال عضو شوید.")
