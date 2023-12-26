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

from aiogram.types import CallbackQuery, ParseMode, InlineKeyboardMarkup

from keyboards.inline.main_menu import menu_structure, create_markup
from keyboards.inline.my_referral import referral_menu_markup
from loader import bot, dp, db_utils
from utils import bot_tools
from utils.converters import convert_english_digits_to_farsi, convert_to_shamsi
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
        formmated_account = convert_english_digits_to_farsi(str(account))
        formatted_balance = convert_english_digits_to_farsi(str(balance))
        formatted_referral_count = convert_english_digits_to_farsi(str(referral_count))
        formatted_join_on = convert_to_shamsi(join_on.date())
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
    elif callback_data == "buy":
        try:
            markup = await bot_tools.display_plans()
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
        try:
            await bot.answer_callback_query(call.id)
            sub_id = int(callback_data.split("_")[1])
            markup = await bot_tools.display_tariffs(sub_id)
            title = "توضیحات طرح ها در اینجا قرار میگیرد."
            await bot_tools.edit_or_send_new(
                chat_id=chat_id, new_text=title, reply_markup=markup
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
            markup = InlineKeyboardMarkup()
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

    else:
        # If the callback_data doesn't match any known menu, log it and inform the user
        print(callback_data)
        prompt_text = "منو تعریف نشده است."
        await bot.answer_callback_query(call.id, text=prompt_text)
