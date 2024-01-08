import traceback

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    ContentTypes,
    ParseMode,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.utils.exceptions import MessageToDeleteNotFound

from data.config import ADMINS
from database.redis_tools import get_shared_data
from keyboards.inline.main_menu import create_markup
from keyboards.reply import remove_keyboard
from loader import dp, bot, db_utils
from states.wait_for_payment_receipt import InputPhotoState
from utils.bot_tools import edit_or_send_new, escape_markdown_v2
from utils.converters import convert_english_digits_to_farsi
from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


@dp.message_handler(lambda message: message.text == "❌ لغو", state="*")
async def cancel_state(message: types.Message, state: FSMContext) -> None:
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


@dp.callback_query_handler(
    lambda call: call.data.startswith("cancelPurchase_"),
    state=InputPhotoState.wait_for_photo,
)
async def handle_purchase(call: CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(call.id)
        purchase_id = int(call.data.split("_")[1])
        await state.finish()

        # Update the purchase status in the database
        update_purchase_status = (
            "UPDATE PurchaseHistory SET Status = 'cancel' WHERE PurchaseID=%s;"
        )
        await db_utils.execute_query(
            query=update_purchase_status, params=(purchase_id,)
        )

        logger.info(
            f"Purchase status updated to 'cancel' for PurchaseID: {purchase_id}"
        )

        # Generate the main menu markup
        menu, text = await create_markup(menu_key="users_main_menu")

        # Send the main menu to the user
        await edit_or_send_new(
            chat_id=call.message.chat.id, new_text=text, reply_markup=menu
        )
    except Exception as e:
        logger.error(f"Error in handle_purchase: {e}")
        # Handle the error appropriately (e.g., send an error message to the user)
        await call.message.reply("An error occurred. Please try again later.")

        # Optionally re-raise the exception if you want it to be caught by a higher-level error handler
        # raise e


@dp.message_handler(
    content_types=ContentTypes.PHOTO, state=InputPhotoState.wait_for_photo
)
async def handle_receipt_photo(message: types.Message, state: FSMContext):
    """
    Handle the photo message sent by the user when in the 'waiting_for_photo' state.

    This function performs the following tasks:
    1. Deletes the photo from the user's chat after it's received.
    2. Notifies the user about the receipt and the ongoing processing of the photo.
    3. Sends the photo to the admin(s) with accompanying details and action buttons.

    Args:
    - message (types.Message): The photo message sent by the user.
    - state (FSMContext): The current FSM state of the user's conversation with the bot.

    Returns:
    None
    """
    chat_id = message.chat.id
    # Extract the file_id of the highest resolution photo from the message
    photo_file_id = message.photo[-1].file_id
    try:
        purchase_data = await get_shared_data(chat_id=chat_id, key="purchase_data")
        logger.info(f"Purchase data retrieved for chat ID {chat_id}: {purchase_data}")
        amount = purchase_data["amount"]
        # Delete the received photo from the user's chat
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)

        # Notify the user about the photo receipt and ongoing processing
        user_notification_msg = (
            "✅ رسید شما دریافت شد. همکاران ما به‌زودی آن را بررسی می‌کنند."
            " در صورت صحت پرداخت، خرید شما به صورت خودکار انجام خواهد شد و تنظیمات را دریافت خواهید کرد."
        )
        await edit_or_send_new(chat_id=chat_id, new_text=user_notification_msg)

        # Reset the FSM state to its default value after photo processing
        await state.finish()
        # Prepare the message text to be sent to the admin(s)
        amount_md = escape_markdown_v2(str(amount))

        # Define the SQL query to get the wallet balance
        sql_query = "SELECT UserID FROM BotUsers WHERE ChatID = %s"

        (user_account,) = await db_utils.fetch_data(
            sql_query, (chat_id,), fetch_one=True
        )
        admin_text = (
            f"🔊 *مبلغ{convert_english_digits_to_farsi('{:,}'.format(int(amount_md)))} هزار  تومان "
            f"توسط شناسه کاربری {user_account} پرداخت شده است\\. "
            "بعد از صحت سنجی تایید کنید\\.*\n\n"
            "⌛ وضعیت\\: _در انتظار تایید_\n\n"
        )

        # Prepare the inline keyboard with confirmation and rejection buttons for the admin(s)
        admin_markup = InlineKeyboardMarkup(row_width=2)
        confirm_button = InlineKeyboardButton(
            "✅ تأیید", callback_data=f"confirm_payment_{chat_id}"
        )
        reject_button = InlineKeyboardButton(
            "❌ رد", callback_data=f"reject_payment_{chat_id}"
        )
        admin_markup.add(confirm_button, reject_button)

        # Send the photo and the message text to the specified admin(s)
        for admin in ADMINS:
            new_msg = await bot.send_photo(
                admin,
                photo_file_id,
                admin_text,
                reply_markup=admin_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            await db_utils.store_message_id(
                chat_id=admin, message_id=new_msg.message_id
            )
    except MessageToDeleteNotFound:
        logger.error("Message to delete not found!")
    except Exception as err:
        error_traceback = traceback.format_exc()
        logger.error(
            f"An unexpected error occurred while registering the user: {err}\n{error_traceback}"
        )
