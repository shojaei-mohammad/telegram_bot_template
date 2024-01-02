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
import re
import traceback
import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ContentType
from aiogram.utils.exceptions import TelegramAPIError

from data.config import BASE_REFERRAL_LINK
from database.redis_tools import set_shared_data, get_shared_data, delete_shared_data
from keyboards.inline.main_menu import create_markup
from loader import dp, bot, db_utils
from states.wait_for_custom_name import InputCustomName
from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


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
        referrer_id = args.replace("REF-", "")

    try:
        # Check if the user exists in the BotUsers table
        user_exists = await db_utils.check_user_exists(chat_id=chat_id)
        if user_exists:
            logger.info(f"Chat-id {chat_id} has already registered.")
            markup, menu_text = await create_markup(menu_key="users_main_menu")
            # Send the message with the appropriate menu
            last_msg = await bot.send_message(
                chat_id=chat_id, text=menu_text, reply_markup=markup
            )
            await db_utils.store_message_id(chat_id, last_msg.message_id)
            return

        elif message.text == "/start" or str(args).startswith("REF"):
            logger.info(
                f"New user detected, Going through registration for Chat-id: {chat_id}"
            )
            if referrer_id:
                logger.info(
                    f"User came in with referral link, referred by: {referrer_id}"
                )
                check_referrer_query = (
                    "SELECT COUNT(*) FROM BotUsers WHERE ReferralCode = %s"
                )
                (referrer_count,) = await db_utils.fetch_data(
                    query=check_referrer_query, params=(referrer_id,), fetch_one=True
                )

                if referrer_count == 0:
                    await message.reply(
                        text="🌌 اوپس! به نظر می‌رسد لینک معرف شما از کهکشان راه شیری خارج شده. لطفا دوباره بررسی "
                        "کنید و با یک لینک صحیح به سیاره ما بازگردید!"
                    )
                    return
                else:
                    await set_shared_data(
                        chat_id=chat_id, key="referrer_id", value=referrer_id
                    )
                    logger.info(
                        f"Chat-id:{chat_id} started the bot via referral link, Referred By: {referrer_id}"
                    )

        await message.answer(
            text="یک نام کاربری دلخواه وارد نمایید. توجه نمایید که نام کاربری باید حتما "
            "با حروف انگلیسی شروع شود و حداکثر ۱۵ کارکتر باشد."
        )
        await InputCustomName.wait_for_photo.set()

    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"An unexpected error occurred: {e}\n{error_traceback}")


@dp.message_handler(
    content_types=ContentType.TEXT, state=InputCustomName.wait_for_photo
)
async def handle_custom_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    name = message.chat.first_name
    last_name = message.chat.last_name
    username = message.chat.username
    custom_name = message.text

    # Get the referrer id
    referrer_id = await get_shared_data(chat_id=chat_id, key="referrer_id")

    # clear the shared data
    await delete_shared_data(chat_id=chat_id, key="referrer_id")

    # Check if the input starts with English letters and has a max length of 15
    if re.match("^[A-Za-z].{0,14}$", custom_name):
        await register_user(
            chat_id=chat_id,
            name=name,
            lastname=last_name,
            username=username,
            custom_name=custom_name,
            referrer_id=referrer_id,
        )
        menu, text = await create_markup(menu_key="users_main_menu")
        last_msg = await bot.send_message(text=text, chat_id=chat_id, reply_markup=menu)
        await db_utils.store_message_id(message.chat.id, last_msg.message_id)
        await state.finish()
    else:
        # Send a message back if the input is invalid
        await message.reply(
            "نام کاربری وارد شده صحیح نمی‌باشد. لطفا یک نامی وارد کنید که با حروف انگلیسی شروع شود و "
            "حداکثر ۱۵ کارکتر داشته باشد."
        )


async def register_user(
    chat_id: int,
    name: str,
    lastname: str,
    username: str,
    custom_name: str,
    referrer_id: str = None,
) -> None:
    """
    Register a user in the database.

    Args:
        custom_name(str): User's custome name for thier service.
        chat_id (int): User's chat ID.
        name (str): User's first name.
        lastname (str): User's last name.
        username (str): User's username.
        referrer_id (str, optional): Referral token (if available)

    Returns:
        None
    """
    id_parts = str(uuid.uuid4()).split("-")
    referral_code = "-".join(id_parts[:2])
    referral_link = BASE_REFERRAL_LINK + referral_code

    try:
        # SQL query to insert a new user into the table
        registration_query = """
        INSERT INTO BotUsers (ChatID, Name, Lastname, Username, CustomName, ReferralCode, ReferredBy, ReferralLink)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Parameters for the SQL query
        params = (
            chat_id,
            name,
            lastname,
            username,
            custom_name,
            referral_code,
            referrer_id,
            referral_link,
        )
        await db_utils.execute_query(registration_query, params)
        logger.info(f"The user with {chat_id} registered successfully")

        # Update the refferer count
        if referrer_id:
            update_referral_count_query = """
            UPDATE BotUsers SET ReferralCount = ReferralCount + 1 WHERE ReferralCode = %s
            """
            await db_utils.execute_query(update_referral_count_query, (referrer_id,))
            logger.info(
                f"The Referral count increased for user with referral code: {referrer_id}"
            )

    except TelegramAPIError as e:
        error_traceback = traceback.format_exc()
        logger.error(
            f"An unexpected API error occurred while registering the user: {e}\n{error_traceback}"
        )
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(
            f"An unexpected error occurred while registering the user: {e}\n{error_traceback}"
        )
