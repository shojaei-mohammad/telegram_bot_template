import datetime

from aiogram.types import InlineKeyboardMarkup

from utils import converters as convert
from utils.bot_tools import edit_or_send_new, add_return_buttons
from utils.hiddify import HiddifyClient
from utils.logger import LoggerSingleton
from .base_service_handler import IServiceDetail

logger = LoggerSingleton.get_logger()


class HiddifyServiceDetail(IServiceDetail):
    async def show_detail(
        self,
        chat_id,
        title,
        subscription_url: str,
        client_name: str,
        url: str,
        username: str,
        password: str,
    ):
        """
        Displays detailed information about a Hiddify service subscription.

        Args:
            title: short explnation about the service
            chat_id: The chat ID where the message should be sent.
            subscription_url: URL of the subscription.
            client_name: Name of the client for whom details are being fetched.
            url: Base URL of the Hiddify service.
            username: Admin key or username for authentication.
            password: Password for authentication (unused in current implementation).

        Returns:
            None. Sends a message to the specified chat_id with subscription details.
        """
        try:
            # Initialize the client and fetch data
            client = HiddifyClient(base_url=url, admin_key=username)
            client_data = await client.get_user_detail(uuid=client_name)

            # Convert and format data
            start_date_str = client_data["start_date"]
            formatted_used_data = convert.convert_english_digits_to_farsi(
                str(client_data["current_usage_GB"])
            )

            # Calculate expiration date
            if start_date_str is None:
                expire_date_str = "استفاده نشده"
            else:
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
                package_days = client_data["package_days"]
                expire_date = start_date + datetime.timedelta(days=package_days)
                expire_date_str = convert.convert_to_shamsi(expire_date)

            # Create the service text message
            service_text = (
                f"{title}\n\n"
                f"📧 نام کاربری: {client_data['name']} \n"
                f"⏳ حجم مصرف شده: {formatted_used_data} GB\n "
                f"⏰ تاریخ انقضا: {expire_date_str} \n"
                f"🔗 لینک سابسکریپشن: \n{subscription_url}"
            )

            # Prepare the markup and send the message
            markup = InlineKeyboardMarkup()
            add_return_buttons(
                markup=markup, back_callback="users_main_menu", include_main_menu=False
            )
            await edit_or_send_new(
                chat_id=chat_id, new_text=service_text, reply_markup=markup
            )
            logger.info(f"Service details sent to chat ID {chat_id}")

        except Exception as e:
            logger.error(f"Error in show_detail: {e}")
