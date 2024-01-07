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
import json
import os
import traceback
from datetime import datetime
from decimal import Decimal

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import (
    MessageToEditNotFound,
    MessageNotModified,
    MessageCantBeEdited,
)

from data.config import CARD_HOLDER, CARD_NUMBER
from keyboards.inline.return_buttons import add_return_buttons
from loader import bot, db_utils
from utils.converters import convert_to_shamsi
from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()

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
    last_msg_id = await db_utils.get_last_message_id(chat_id)
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
            await db_utils.store_message_id(chat_id=chat_id, message_id=message_id)
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
                await db_utils.store_message_id(chat_id=chat_id, message_id=message_id)


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


async def display_plans(subscription_type: str) -> InlineKeyboardMarkup:
    """
    Fetches and displays available subscription plans.

    This function queries the database for available subscription plans and
    displays them to the user as inline buttons. Additional control buttons
    like 'Back' and 'Main Menu' are also included for navigation.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup with subscription plans and control buttons.
    """
    markup = InlineKeyboardMarkup()
    try:
        fetch_plans_query = "SELECT SubscriptionID, SubscriptionName FROM Subscriptions WHERE SubscriptionType = %s;"
        subs = await db_utils.fetch_data(fetch_plans_query, (subscription_type,))

        for sub_id, sub_name in subs:
            button = InlineKeyboardButton(
                f"{sub_name}", callback_data=f"sub_{sub_id}_{subscription_type}"
            )
            markup.add(button)

        add_return_buttons(markup=markup, back_callback="buy")
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error fetching subscription plans: {e}\n{error_traceback}")

    return markup


async def display_tariffs(
    sub_id: int, subscription_type: str
) -> InlineKeyboardMarkup | None:
    """
    Fetches and displays available tariffs for a selected subscription plan.

    Args:
        subscription_type: type of subscription `limited` or `unlimited`
        sub_id (int): The ID of the selected subscription plan.

    Returns:
        InlineKeyboardMarkup: An inline keyboard markup containing buttons for each tariff,
                              or None if no tariffs are found.

    Raises:
        Exception: If an error occurs during database fetch operation.
    """
    markup = InlineKeyboardMarkup()
    try:
        fetch_tariffs_query = """
        SELECT TariffID, TariffDescription, Price
        FROM Tariffs
        INNER JOIN Subscriptions ON Tariffs.SubscriptionID = Subscriptions.SubscriptionID
        WHERE Subscriptions.SubscriptionID = %s;
        """
        tariffs = await db_utils.fetch_data(fetch_tariffs_query, (sub_id,))

        # Check if tariffs are available
        if not tariffs:
            logger.info(f"No tariffs found for subscription ID {sub_id}")
            return None  # Return None if no tariffs are found

        # Loop through tariffs and add buttons to markup
        for tariff_id, tariff_name, price in tariffs:
            button = InlineKeyboardButton(
                f"{tariff_name}",
                callback_data=f"tariff_{tariff_id}_{sub_id}_{subscription_type}_{int(price)}",
            )
            markup.add(button)

        # Add return button to markup
        add_return_buttons(markup=markup, back_callback=f"buy_{subscription_type}")

    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(
            f"Error fetching tariffs for subscription ID {sub_id}: {e}\n{error_traceback}"
        )
        raise  # Re-raise the exception to handle it in the calling context

    return markup


async def display_countries(
    tariff_id: int, sub_id: int, subscription_type: str, price: int
) -> InlineKeyboardMarkup:
    """
    Generates a markup of countries for a given subscription ID and tariff ID.

    This function fetches distinct countries associated with a specific subscription
    and creates an inline keyboard markup with each country as a button.

    Args:
    tariff_id (int): The ID of the tariff.
    sub_id (int): The ID of the subscription.
    subscription_type (str): The type of the subscription.

    Returns:
    InlineKeyboardMarkup: A markup of buttons for each distinct country.
    """
    # SQL query to fetch distinct countries for a subscription
    get_country_info_query = """
    SELECT CountryID, CountryName
    FROM Countries
    WHERE SubscriptionID = %s;
    """
    try:
        # Fetch distinct countries from the database
        countries = await db_utils.fetch_data(
            query=get_country_info_query, params=(sub_id,)
        )
        logger.info(f"Fetched countries for SubscriptionID {sub_id}")

        # Create a markup with buttons for each country
        markup = InlineKeyboardMarkup()
        for country_id, country_name in countries:
            button = InlineKeyboardButton(
                f"{country_name}",
                callback_data=f"purchase_{tariff_id}_{country_id}_{price}",
            )
            markup.add(button)

        # Add a return button to the markup
        add_return_buttons(
            markup=markup, back_callback=f"sub_{sub_id}_{subscription_type}"
        )

        return markup
    except Exception as e:
        logger.error(f"Error in display_countries: {e}")
        raise


def load_faqs():
    """
    Loads FAQ data from a JSON file.

    This function reads FAQs from a JSON file located in the 'data' directory
    relative to the script's parent directory. It returns a dictionary
    of FAQs categorized by platform.

    Returns:
        dict: A dictionary containing FAQs categorized by platform.

    Raises:
        FileNotFoundError: If the FAQs JSON file is not found.
        JSONDecodeError: If there's an error parsing the JSON file.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)  # One level up from current directory
        json_file = os.path.join(parent_dir, "data/faqs.json")

        with open(json_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("FAQs JSON file not found.")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing FAQs JSON file: {e}")
        raise


async def display_services(chat_id) -> InlineKeyboardMarkup:
    """
    Asynchronously retrieves active services for a given chat ID and generates an inline keyboard markup.

    Args:
        chat_id (int/str): The unique identifier for a chat.

    Returns:
        InlineKeyboardMarkup: A markup of inline keyboard buttons, each representing an active service.

    Raises:
        Exception: If an error occurs during database query or data processing.
    """

    # SQL query to fetch active services based on chat_id
    get_services_query = """
        SELECT 
            us.TariffID,
            us.UserSubscriptionName,
            t.TariffName
            s.Platform
        FROM 
            UserSubscriptions us
        INNER JOIN 
            Tariffs t ON t.TariffID = us.TariffID
        INNER JOIN 
            Subscriptions s ON s.SubscriptionID = t.SubscriptionID
        WHERE 
            us.Status = 'active'
            AND us.ChatID = %s;
    """

    try:
        # Fetching data from the database
        result = await db_utils.fetch_data(query=get_services_query, params=(chat_id,))
        markup = InlineKeyboardMarkup()

        if result:
            for tariff_id, email_name, tariff_name, platform in result:
                # Creating a button for each service
                button = InlineKeyboardButton(
                    f"{tariff_name}",
                    callback_data=f"service_{tariff_id}_{email_name}_{platform}",
                )
                markup.add(button)

            # Adding return buttons to the markup
            add_return_buttons(
                markup=markup, back_callback="users_main_menu", include_main_menu=False
            )

        return markup

    except Exception as e:
        # Logging the exception
        error_detail = traceback.format_exc()
        logger.error(f"Error in display_services: {e}\nDetails:{error_detail}")
        raise


def generate_faq_buttons(platform: str) -> InlineKeyboardMarkup:
    """
    Generates inline keyboard buttons for FAQs based on the specified platform.

    Args:
        platform (str): The platform for which FAQs are to be displayed ('IOS' or 'android').

    Returns:
        InlineKeyboardMarkup: An inline keyboard markup containing buttons for each FAQ.

    Raises:
        KeyError: If the platform is not found in the FAQs data.
    """
    try:
        markup = InlineKeyboardMarkup()
        faqs = load_faqs()  # Load FAQs from the JSON file

        for index, faq in enumerate(faqs[platform]):
            button = InlineKeyboardButton(
                text=faq["question"], callback_data=f"faqAnswer_{platform}_{index}"
            )
            markup.add(button)

        add_return_buttons(markup=markup, back_callback="faqs")
        return markup
    except KeyError as e:
        logger.error(f"Platform '{platform}' not found in FAQs data: {e}")
        raise


async def create_invoice(
    tariff_id: int,
    country_id: int,
    current_additional_users: int = 0,
    current_price: Decimal = None,
    additional_volume: int = 0,
):
    get_tariff_info_query = """
    SELECT
        Tariffs.SubscriptionID, Tariffs.TariffName, Tariffs.Price, Tariffs.Duration,
        Tariffs.Volume,Subscriptions.SubscriptionDescription,
        Subscriptions.SubscriptionType, Subscriptions.AddedPricePerUser, Subscriptions.PricePerGig,
        Subscriptions.VolumeExtendable, Subscriptions.UserExtendable, Subscriptions.NumberOfUsers,
        Subscriptions.Platform , Countries.CountryID, Countries.CountryName
    FROM
        Tariffs
    INNER JOIN
        Subscriptions ON Tariffs.SubscriptionID = Subscriptions.SubscriptionID
    INNER JOIN
        Countries ON Tariffs.SubscriptionID = Countries.SubscriptionID AND Countries.CountryID=%s
    WHERE TariffID = %s
    """
    result = await db_utils.fetch_data(
        query=get_tariff_info_query,
        params=(
            country_id,
            tariff_id,
        ),
        fetch_one=True,
    )
    if result:
        (
            sub_id,
            name,
            price,
            duration,
            volume,
            description,
            subscription_type,
            price_per_user,
            price_per_gig,
            volume_extendable,
            user_extendable,
            users,
            platform,
            country_id,
            country_name,
        ) = result
        # If current_price is None, use the base price from the database
        if current_price is None:
            current_price = price

        # Calculate the additional cost
        additional_cost_for_users = 0
        if current_additional_users > 0:
            price_increase_per_user = Decimal(price_per_user) / Decimal(100)
            additional_cost_for_users = (
                price * price_increase_per_user * Decimal(current_additional_users)
            )

        additional_cost_per_gig = 0
        if additional_volume > 0:
            additional_cost_per_gig = Decimal(price_per_gig) * Decimal(
                additional_volume
            )

        # Calculate the new price
        new_price = price + additional_cost_for_users + additional_cost_per_gig

        # formatting invoice
        invoice_date = convert_to_shamsi(datetime.now())

        # Calculate the total number of users for display
        total_users = users + current_additional_users
        formatted_new_price = "{:,}".format(int(new_price))
        invoice_text = f"""
        🧾 صورت‌حساب 🧾

        مشتری گرامی،
        از انتخاب شما متشکریم! جزئیات خرید طرح شما به شرح زیر است:

        🔹 نام طرح: {name}
        🔹 کشور: {country_name}
        🔹 تعداد کاربر: {'نامحدود' if users == 0 else total_users}
        🔹 حجم اضافه: {additional_volume} GB
        🔹 قیمت: {formatted_new_price} تومان
        📅 تاریخ صورت‌حساب: {invoice_date}
        💳 جزئیات پرداخت:
        شماره کارت: <code>{CARD_NUMBER}</code>
        نام دارنده کارت: {CARD_HOLDER}
        <code>{int(new_price)}</code>
        """
        markup = InlineKeyboardMarkup()
        if user_extendable:
            add_user_txt_btn = InlineKeyboardButton(
                text="افزدون کاربر", callback_data="NoAction"
            )

            # Update the callback data for the buttons
            add_user_btn = InlineKeyboardButton(
                text="➕",
                callback_data=f"addUser_{tariff_id}_{current_additional_users}_{new_price}_"
                f"{users}_{additional_volume}_{country_id}",
            )
            deduct_user_btn = InlineKeyboardButton(
                text="➖",
                callback_data=f"deductUser_{tariff_id}_{current_additional_users}_"
                f"{new_price}_{users}_{additional_volume}_{country_id}",
            )
            markup.add(add_user_btn, add_user_txt_btn, deduct_user_btn)

        if volume_extendable:
            add_volume_txt_btn = InlineKeyboardButton(
                text="افزدون حجم", callback_data="NoAction"
            )
            add_volume_btn = InlineKeyboardButton(
                text="➕",
                callback_data=f"addVolume_{tariff_id}_{additional_volume}_"
                f"{new_price}_{current_additional_users}_{country_id}",
            )
            deduct_volume_btn = InlineKeyboardButton(
                text="➖",
                callback_data=f"deductVolume_{tariff_id}_{additional_volume}_"
                f"{new_price}_{current_additional_users}_{country_id}",
            )
            markup.add(add_volume_btn, add_volume_txt_btn, deduct_volume_btn)
        if volume is not None:
            total_volume = additional_volume + volume
        else:
            total_volume = 0
        confirm_btn = InlineKeyboardButton(
            text="✅ پرداخت کردم",
            callback_data=f"paid_{tariff_id}_{total_users}_{total_volume}_{int(new_price)}_{platform}_{duration}",
        )
        markup.add(confirm_btn)
        add_return_buttons(
            markup=markup,
            back_callback=f"tariff_{tariff_id}_{sub_id}_{subscription_type}_{int(price)}",
        )
        return invoice_text, markup


async def find_least_loaded_server(tariff_id):
    """
    Finds and returns the least loaded server based on the user count for a given tariff ID.

    Args:
        tariff_id (int): The Tariff ID to match servers with.

    Returns:
        dict: A dictionary containing the server details (IP, username, password, inbound ID) of the least loaded server.
    """

    get_server_info_query = """
    SELECT
        Servers.ServerID, Servers.ServerIP, Servers.Username, Servers.Password, Servers.InboundID
    FROM
        Servers
    INNER JOIN
        Tariffs ON Tariffs.SubscriptionID = Servers.SubscriptionID
    WHERE
        Tariffs.TariffID = %s
    ORDER BY
        Servers.UserCount ASC
    LIMIT 1;
    """

    result = await db_utils.fetch_data(
        query=get_server_info_query, params=(tariff_id,), fetch_one=True
    )

    if result:
        return {
            "ServerID": result[0],
            "ServerIP": result[1],
            "Username": result[2],
            "Password": result[3],
            "InboundID": result[4],
        }
    else:
        return None  # or handle the case where no server is found
