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
import traceback
import uuid
from datetime import datetime

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils.exceptions import TelegramAPIError

from core.data import settings
from core.database.redis_tools import (
    set_shared_data,
)
from core.keyboards.main_menu import create_markup
from core.utils.logger import LoggerSingleton
from loader import dp, bot, db_utils

logger = LoggerSingleton.get_logger()


@dp.message_handler(CommandStart(deep_link=None))
async def bot_start(message: types.Message) -> None:
    """
    Begin the interaction with the bot.

    This handler gets activated when a user starts the bot, possibly with a referral link.


    Args:
        message (types.Message): The message object from the user starting the bot.

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
            "با حروف انگلیسی شروع شود و حداکثر ۱۰ کارکتر باشد."
            "همچنین نباید از کارکترهای خاص استفاده نمایید."
        )

    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"An unexpected error occurred: {e}\n{error_traceback}")


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
    referral_link = settings.BASE_REFERRAL_LINK + referral_code

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

        # SQL query to insert a referral discount into the Discounts table
        insert_discount_query = """
        INSERT INTO Discounts (DiscountCode, DiscountType, DiscountValue, StartDate, OwnerChatID, IsReferral)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        # Parameters for the discount insert query
        discount_params = (
            referral_code,
            "Percentage",
            10,
            datetime.now(),
            chat_id,
            True,
        )
        await db_utils.execute_query(insert_discount_query, discount_params)
        logger.info(f"Referral discount created for user with chat ID: {chat_id}")

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
