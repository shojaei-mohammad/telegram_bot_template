"""
defualt.py - Handle callback queries for the Telegram bot.

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
import traceback
from decimal import Decimal
from uuid import uuid4

from aiogram.types import (
    CallbackQuery,
    ParseMode,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from data import config
from database.redis_tools import set_shared_data, get_shared_data, delete_shared_data
from keyboards.inline.main_menu import menu_structure, create_markup
from keyboards.inline.my_referral import referral_menu_markup
from loader import bot, dp, db_utils
from states.wait_for_payment_receipt import InputPhotoState
from user_handler.factory import CreateUserFactory
from utils import bot_tools
from utils import converters as convert
from utils.logger import LoggerSingleton

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
    elif callback_data == "earning":
        await bot.answer_callback_query(call.id)
        user_info_query = """
        SELECT
            UserID, WalletBalance, ReferralCount, ReferralLink,JoinOn
        FROM
            BotUsers
        WHERE
            ChatID = %s;
        """
        results = await db_utils.fetch_data(
            query=user_info_query, params=(chat_id,), fetch_one=True
        )
        account, balance, referral_count, referral_link, join_on = results
        formmated_account = convert.convert_english_digits_to_farsi(str(account))
        formatted_balance = convert.convert_english_digits_to_farsi(str(balance))
        formatted_referral_count = convert.convert_english_digits_to_farsi(
            str(referral_count)
        )
        formatted_join_on = convert.convert_to_shamsi(join_on.date())
        message_text = (
            f"👤 شناسه کاربری : {formmated_account}\n"
            f"💰 موجودی کیف پول: {formatted_balance} تومان\n"
            f"👥 تعداد معرفی‌ها: {formatted_referral_count} نفر\n"
            f"🗓️ تاریخ عضویت: {formatted_join_on}\n"
            f"🔗 لینک معرف شما:\n `{referral_link}`\n\n"
        )
        message_text += "متن توضیات شما اینجا قرار خواهد گرفت"
        await bot_tools.edit_or_send_new(
            chat_id=chat_id,
            new_text=message_text,
            reply_markup=referral_menu_markup,
            parsmode=ParseMode.MARKDOWN_V2,
        )
    elif callback_data.startswith("buy_"):
        """
        Displays the subscriptions based on user selectin `limited` or `unlimited`
        """
        try:
            subscription_type = callback_data.split("_")[1]
            markup = await bot_tools.display_plans(subscription_type=subscription_type)
            title = "توضیحات طرح ها در اینجا قرار میگیرد."
            await bot_tools.edit_or_send_new(
                chat_id=chat_id, new_text=title, reply_markup=markup
            )
            await bot.answer_callback_query(call.id)
        except Exception as e:
            error_text = "هنگام دریافت طرح ها خطایی رخ داده است. لطفا دوباره تلاش کنید و یا با پشتیبانی تماس بگیرید"
            await bot.answer_callback_query(call.id, error_text, show_alert=True)
            error_trackback = traceback.format_exc()
            logger.error(f"Error displaying plans: {e}\n{error_trackback}")
    elif callback_data.startswith("sub_"):
        """
        Displays all available subscription related to limited or unlimited based on user selection
        """
        sub_id = None
        try:
            sub_id = int(callback_data.split("_")[1])
            subscription_type = callback_data.split("_")[2]
            markup = await bot_tools.display_tariffs(sub_id, subscription_type)
            if markup:
                await bot.answer_callback_query(call.id)
                title = "توضیحات طرح ها در اینجا قرار میگیرد."
                await bot_tools.edit_or_send_new(
                    chat_id=chat_id, new_text=title, reply_markup=markup
                )
            else:
                await bot.answer_callback_query(
                    call.id, "تعرفه ای یافت نشد!", show_alert=True
                )
        except ValueError:
            error_text = "هنگام دریافت تعرفه ها خطایی رخ داده است. لطفا دوباره تلاش کنید و یا با پشتیبانی تماس بگیرید"
            await bot.answer_callback_query(call.id, error_text, show_alert=True)
            error_trackback = traceback.format_exc()
            logger.error(
                f"Invalid subscription ID format in callback data.\n{error_trackback}"
            )
            # Handle the invalid subscription ID format (e.g., send an error message to the user)
        except Exception as e:
            error_text = "هنگام دریافت تعرفه ها خطایی رخ داده است. لطفا دوباره تلاش کنید و یا با پشتیبانی تماس بگیرید"
            await bot.answer_callback_query(call.id, error_text, show_alert=True)
            error_trackback = traceback.format_exc()
            logger.error(
                f"Error displaying tariffs for subscription ID {sub_id}: {e}\n{error_trackback}"
            )
    elif callback_data.startswith("tariff_"):
        """
        Display the available counries
        """
        await bot.answer_callback_query(call.id)
        await bot.answer_callback_query(call.id)
        _, tariff_id, sub_id, subscription_type, price = callback_data.split("_")
        tariff_id = int(tariff_id)
        sub_id = int(sub_id)
        price = int(price)
        markup = await bot_tools.display_countries(
            tariff_id, sub_id, subscription_type, price
        )
        title_text = "کشور مورد نظر خودتان را انتخاب نمایید."
        await bot_tools.edit_or_send_new(
            chat_id=chat_id,
            new_text=title_text,
            reply_markup=markup,
            parsmode=ParseMode.HTML,
        )
    elif callback_data.startswith("purchase_"):
        _, tariff_id, country_id, price = callback_data.split("_")

        if int(price) == 0:
            check_user_right_query = """
            SELECT
                UsedTestAcount
            FROM
                BotUsers
            WHERE
                ChatID=%s;
            """
            (has_right,) = await db_utils.fetch_data(
                query=check_user_right_query, params=(chat_id,), fetch_one=True
            )
            if has_right:
                await bot.answer_callback_query(
                    call.id,
                    text="شما یکبار از این سرویس استفاده کرده‌اید.",
                    show_alert=True,
                )
                return
            else:
                try:
                    get_tariff_info = """
                    SELECT
                        Tariffs.TariffName, Tariffs.Duration, Tariffs.Volume,
                        Subscriptions.NumberOfUsers, Subscriptions.Platform,
                        Servers.ServerIP, Servers.Username, Servers.Password, Servers.InboundID
                    FROM
                        Tariffs
                    INNER JOIN
                        Subscriptions ON Subscriptions.SubscriptionID=Tariffs.SubscriptionID
                    INNER JOIN
                        Servers ON Servers.SubscriptionID = Tariffs.SubscriptionID
                    WHERE
                        Tariffs.TariffID=%s
                    """
                    result = await db_utils.fetch_data(
                        query=get_tariff_info, params=(tariff_id,), fetch_one=True
                    )
                    if not result:
                        await bot.answer_callback_query(
                            call.id,
                            text="اطلاعات سفارش یافت نشد. با پشتیبانی تماس بگیرید.",
                            show_alert=True,
                        )
                        return
                    (
                        plan_name,
                        duration,
                        total_volume,
                        total_users,
                        platform,
                        url,
                        username,
                        password,
                        inbound_id,
                    ) = result
                    unique_id = str(uuid4()).split("-")[4]

                    get_user_name_query = (
                        "SELECT CustomName FROM BotUsers WHERE ChatID=%s;"
                    )
                    (name,) = await db_utils.fetch_data(
                        query=get_user_name_query, params=(chat_id,), fetch_one=True
                    )
                    if platform == "xui":
                        epoch_duration = convert.convert_days_to_epoch(duration)
                        total_volume_bytes = convert.gb_to_bytes(total_volume)
                        setting = {
                            "inbound_id": inbound_id,
                            "email": f"{name}-{unique_id}-{chat_id}",
                            "limit_ip": total_users,
                            "total_gb": total_volume_bytes,
                            "expiry_time": epoch_duration,
                        }
                    else:
                        logger.error(
                            f"Could not get the server info from tariff id {tariff_id}"
                        )
                        return

                    # create user
                    handler = CreateUserFactory.get_create_user_handler(platform)
                    subscription_url = await handler.create_user(
                        chat_id=chat_id,
                        url=url,
                        username=username,
                        password=password,
                        settings=setting,
                    )
                    formatted_volume = f"{total_volume} GB"
                    purchase_text = (
                        "🛍️ اطلاعات خرید شما:\n\n"
                        f"🔢 شماره سفارش: {unique_id}\n"
                        f"💾 حجم: {formatted_volume if total_volume != 0 else 'نامحدود'}\n"
                        f"👥 تعداد کاربر: {total_users}\n"
                        f"🔗 لینک سابسکریپشن:\n{subscription_url}"
                    )

                    update_purchase_status_query = """
                    UPDATE BotUsers SET UsedTestAcount=1 WHERE ChatID=%s;
                    """

                    # Database operations
                    await db_utils.execute_query(
                        query=update_purchase_status_query,
                        params=(chat_id,),
                    )

                    last_msg_id = await db_utils.get_last_message_id(chat_id)
                    await bot.delete_message(chat_id=chat_id, message_id=last_msg_id)
                    await bot.send_message(
                        chat_id=chat_id,
                        text=purchase_text,
                    )
                    await db_utils.reset_last_message_id(chat_id=chat_id)
                    markup, menu_text = await create_markup(menu_key="users_main_menu")
                    # Send the message with the appropriate menu
                    last_msg = await bot.send_message(
                        chat_id=chat_id, text=menu_text, reply_markup=markup
                    )
                    await db_utils.store_message_id(chat_id, last_msg.message_id)
                except Exception as err:
                    error_detail = traceback.format_exc()
                    logger.error(
                        f"An error ocurred during test user creation. {err}\n{error_detail}"
                    )

        else:
            invoice, markup = await bot_tools.create_invoice(
                tariff_id, country_id=country_id
            )
            await bot_tools.edit_or_send_new(
                chat_id=chat_id,
                new_text=invoice,
                reply_markup=markup,
                parsmode=ParseMode.HTML,
            )
    elif callback_data.startswith("addUser") or callback_data.startswith("deductUser"):
        (
            action,
            tariff_id,
            current_additional_users,
            current_price,
            default_user,
            total_volume,
            country_id,
        ) = callback_data.split("_")
        tariff_id = int(tariff_id)
        current_additional_users = int(current_additional_users)
        default_user = int(default_user)
        country_id = int(country_id)

        if action == "addUser":
            if current_additional_users + default_user < config.NUMBER_OF_ALLOWED_USERS:
                current_additional_users += 1
            else:
                # Notify user that they have reached the maximum limit
                await bot.answer_callback_query(
                    call.id,
                    f"حداکثر تعداد مجاز {config.NUMBER_OF_ALLOWED_USERS} کاربر می‌باشد.",
                    show_alert=True,
                )
                return  # Stop further processing

        elif action == "deductUser":
            if current_additional_users > 0:
                current_additional_users = max(0, current_additional_users - 1)
            else:
                # Notify user that they cannot reduce users below zero
                await bot.answer_callback_query(call.id)
                return  # Stop further processing

        # Call create_invoice with the updated current_additional_users
        invoice_text, markup = await bot_tools.create_invoice(
            tariff_id=tariff_id,
            country_id=country_id,
            current_additional_users=current_additional_users,
            current_price=Decimal(current_price),
            additional_volume=int(total_volume),
        )

        # Update the message with the new invoice
        await bot_tools.edit_or_send_new(
            chat_id=chat_id,
            new_text=invoice_text,
            reply_markup=markup,
            parsmode=ParseMode.HTML,
        )
    elif callback_data.startswith("addVolume_") or callback_data.startswith(
        "deductVolume_"
    ):
        (
            action,
            tariff_id,
            total_volume,
            current_price,
            current_additional_users,
            country_id,
        ) = callback_data.split("_")
        tariff_id = int(tariff_id)
        total_volume = int(total_volume)
        country_id = int(country_id)

        if action == "addVolume":
            total_volume += 5
        elif action == "deductVolume":
            if total_volume > 0:
                total_volume = max(0, total_volume - 5)
            else:
                # Notify user that they cannot reduce users below zero
                await bot.answer_callback_query(call.id)
                return  # Stop further processing

        # Call create_invoice with the new adjustment
        invoice_text, markup = await bot_tools.create_invoice(
            tariff_id,
            country_id,
            current_additional_users=int(current_additional_users),
            current_price=Decimal(current_price),
            additional_volume=total_volume,
        )
        # Update the message with the new invoice
        await bot_tools.edit_or_send_new(
            chat_id=chat_id,
            new_text=invoice_text,
            reply_markup=markup,
            parsmode=ParseMode.HTML,
        )
    elif callback_data.startswith("paid_"):
        (
            _,
            tariff_id,
            total_users,
            total_volume,
            amount,
            platform,
            duration,
        ) = callback_data.split("_")

        save_purchase_query = "INSERT INTO PurchaseHistory (ChatID, TariffID, Amount) VALUES (%s, %s, %s);"

        purchase_id = await db_utils.execute_query(
            query=save_purchase_query,
            params=(chat_id, tariff_id, Decimal(amount)),
            fetch_last_insert_id=True,
        )
        get_user_name_query = "SELECT CustomName FROM BotUsers WHERE ChatID=%s;"
        (name,) = await db_utils.fetch_data(
            query=get_user_name_query, params=(chat_id,), fetch_one=True
        )

        purchase_data = {
            "tariff_id": int(tariff_id),
            "users": int(total_users),
            "volume": int(total_volume),
            "amount": int(amount),
            "purchase_id": purchase_id,
            "platform": platform,
            "duration": duration,
            "name": name,
        }
        await set_shared_data(chat_id=chat_id, key="purchase_data", value=purchase_data)
        prompt_text = (
            "لطفا عکس رسید خودتان را ارسال نمایید.\n"
            "در صورتی که منصرف شدید با فشردن دکمه لغو سفارش به منو اصلی بازگردید."
        )
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="لغو سفارش", callback_data=f"cancelPurchase_{purchase_id}"
                    )
                ]
            ]
        )
        await InputPhotoState.wait_for_photo.set()
        await bot_tools.edit_or_send_new(
            chat_id=chat_id, new_text=prompt_text, reply_markup=markup
        )
    elif callback_data.startswith("confirm_payment_"):
        setting = None
        try:
            await bot.answer_callback_query(call.id)
            user_chat_id = callback_data.split("_")[2]
            purchase_data = await get_shared_data(
                chat_id=user_chat_id, key="purchase_data"
            )

            if not purchase_data:
                logger.error(f"No purchase data found for chat ID: {user_chat_id}")
                await bot.answer_callback_query(
                    call.id, text="اطلاعات خرید یافت نشد.", show_alert=True
                )
                return
            await delete_shared_data(chat_id=user_chat_id, key="purchase_data")

            # Extracting purchase data details
            tariff_id = purchase_data["tariff_id"]
            total_users = purchase_data["users"]
            total_volume = purchase_data["volume"]
            purchase_id = purchase_data["purchase_id"]
            platform = purchase_data["platform"]
            duration = purchase_data["duration"]
            name = purchase_data["name"]

            # Notify admins
            for admin in config.ADMINS:
                msg_id = await db_utils.get_last_message_id(chat_id=admin)
                await bot.delete_message(chat_id=admin, message_id=msg_id)
                confirm_text = (
                    "تایید پرداخت\n\n" f"پرداخت با شماره سفارش {purchase_id} تایید شد."
                )
                await bot.send_message(chat_id=admin, text=confirm_text)
                await db_utils.reset_last_message_id(chat_id=admin)
            get_server_info_auery = """
            SELECT
                Servers.ServerIP, Servers.Username, Servers.Password, Servers.InboundID
            FROM
                Servers
            INNER JOIN
                Tariffs ON Tariffs.SubscriptionID = Servers.SubscriptionID
            WHERE
                Tariffs.TariffID = %s;
            """

            result = await db_utils.fetch_data(
                query=get_server_info_auery, params=(tariff_id,), fetch_one=True
            )
            # Handling the result
            if result:
                url, username, password, inbound_id = result
                if platform == "xui":
                    epoch_duration = convert.convert_days_to_epoch(int(duration))
                    total_volume_bytes = convert.gb_to_bytes(total_volume)
                    setting = {
                        "inbound_id": inbound_id,
                        "email": f"{name}-{purchase_id}-{user_chat_id}",
                        "limit_ip": total_users,
                        "total_gb": total_volume_bytes,
                        "expiry_time": epoch_duration,
                    }

            else:
                logger.error(
                    f"Could not get the server info from tariff id {tariff_id}"
                )
                return

            # create user
            handler = CreateUserFactory.get_create_user_handler(platform)
            subscription_url = await handler.create_user(
                chat_id=user_chat_id,
                url=url,
                username=username,
                password=password,
                settings=setting,
            )
            purchase_text = (
                "🛍️ اطلاعات خرید شما:\n\n"
                f"🔢 شماره سفارش: {purchase_id}\n"
                f"💾 حجم: {total_volume} GB\n"
                f"👥 تعداد کاربر: {total_users}\n"
                f"🔗 لینک سابسکریپشن:\n{subscription_url}"
            )

            update_purchase_status_query = """
            UPDATE PurchaseHistory SET Status=4, SubscriptionURL=%s WHERE PurchaseID=%s;
            """

            # Database operations
            await db_utils.execute_query(
                query=update_purchase_status_query,
                params=(subscription_url, purchase_id),
            )

            last_msg_id = await db_utils.get_last_message_id(user_chat_id)
            await bot.delete_message(chat_id=user_chat_id, message_id=last_msg_id)
            await bot.send_message(chat_id=user_chat_id, text=purchase_text)
            await db_utils.reset_last_message_id(chat_id=user_chat_id)
            markup, menu_text = await create_markup(menu_key="users_main_menu")
            # Send the message with the appropriate menu
            last_msg = await bot.send_message(
                chat_id=user_chat_id, text=menu_text, reply_markup=markup
            )
            await db_utils.store_message_id(user_chat_id, last_msg.message_id)
        except Exception as err:
            error_detail = traceback.format_exc()
            logger.error(
                f"Error in processing payment confirmation: {err}\n{error_detail}"
            )
    elif callback_data.startswith("reject_payment_"):
        pass
    elif callback_data.startswith("faqs"):
        try:
            await bot.answer_callback_query(call.id)
            # Extract the device platform ('ios' or 'android') from the callback data
            platform = callback_data.split("_")[1]
            # Generate FAQ buttons based on the selected platform
            markup = bot_tools.generate_faq_buttons(platform)
            # Send or edit a message with the FAQ buttons
            await bot_tools.edit_or_send_new(
                chat_id=chat_id,
                new_text="سوال مورد نظر خودت رو انتخاب کن.",
                reply_markup=markup,
            )
        except Exception as e:
            logger.error(f"Error in 'faqs' callback handling: {e}")
            await bot.answer_callback_query(
                call.id, text="خطایی رخ داده لطفا دوباره تلاش کنید.", show_alert=True
            )
    elif callback_data.startswith("faqAnswer"):
        try:
            _, platform, index = callback_data.split("_")
            index = int(index)  # Convert the index from string to integer
            # Load FAQs and retrieve the answer for the selected question
            faqs = bot_tools.load_faqs()
            answer = faqs[platform][index]["answer"]
            # Create a markup for return button
            markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ حل شد", callback_data="users_main_menu"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="ارسال تیکت پشتیبانی", url=config.SUPPORT_USER_NAME
                        )
                    ],
                ]
            )
            bot_tools.add_return_buttons(
                markup=markup, back_callback=f"faqs_{platform}"
            )
            # Send or edit a message with the selected FAQ answer
            await bot_tools.edit_or_send_new(
                chat_id=chat_id, new_text=answer, reply_markup=markup
            )
        except Exception as e:
            logger.error(f"Error in 'faqAnswer' callback handling: {e}")
            await bot.answer_callback_query(
                call.id, text="خطایی رخ داده لطفا دوباره تلاش کنید.", show_alert=True
            )
    elif callback_data == "NoAction":
        await bot.answer_callback_query(call.id)
    else:
        # If the callback_data doesn't match any known menu, log it and inform the user
        print(callback_data)
        prompt_text = "منو تعریف نشده است."
        await bot.answer_callback_query(call.id, text=prompt_text)
