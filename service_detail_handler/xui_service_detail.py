from aiogram.types import InlineKeyboardMarkup

from utils import converters as convert
from utils.bot_tools import add_return_buttons, edit_or_send_new
from utils.logger import LoggerSingleton
from utils.xui import XUIClient
from .base_service_handler import IServiceDetail

logger = LoggerSingleton.get_logger()


class XUIServiceDetail(IServiceDetail):
    async def show_detail(
        self,
        chat_id,
        subscription_url: str,
        client_name: str,
        url: str,
        username: str,
        password: str,
    ):
        try:
            client = XUIClient(base_url=url)
            client_data = await client.get_user_detail(
                username=username, password=password, client_name=client_name
            )
            total_data_used_byte = client_data["up"] + client_data["down"]
            total_data_used_gb = convert.convert_english_digits_to_farsi(
                str(convert.bytes_to_gb(total_data_used_byte))
            )
            print(convert.convert_epoch_to_days(client_data["expiryTime"]))
            formmated_date = convert.convert_to_shamsi(
                convert.convert_epoch_to_days(client_data["expiryTime"])
            )
            service_text = (
                f"📧 نام کاربری: {client_data['email']} \n"
                f"⏳ حجم مصرف شده: {total_data_used_gb} GB\n "
                f"⏰ تاریخ انقضا: {formmated_date} \n"
                f"🔗 لینک سابسکریپشن: \n{subscription_url}"
            )
            markup = InlineKeyboardMarkup()
            add_return_buttons(
                markup=markup, back_callback="users_main_menu", include_main_menu=False
            )
            await edit_or_send_new(
                chat_id=chat_id, new_text=service_text, reply_markup=markup
            )
        except Exception as err:
            print(err)
