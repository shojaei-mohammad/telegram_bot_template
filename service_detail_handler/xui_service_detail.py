from utils.logger import LoggerSingleton
from utils.xui import XUIClient
from .base_service_handler import IServiceDetail

logger = LoggerSingleton.get_logger()


class XUIServiceDetail(IServiceDetail):
    async def show_detail(
        self, chat_id, client_name: str, url: str, username: str, password: str
    ):
        try:
            client = XUIClient(base_url=url)
            client_data = client.get_user_detail(
                username=username, password=password, client_name=client_name
            )
            print(client_data)
        except Exception as err:
            print(err)
