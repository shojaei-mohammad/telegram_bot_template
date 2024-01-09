import traceback

from utils.hiddify import HiddifyClient
from utils.logger import LoggerSingleton
from .base_panel_handler import IPanel

logger = LoggerSingleton.get_logger()


class HiddifyPanel(IPanel):
    async def create_user(
        self,
        chat_id,
        url: str,
        username: str = None,
        password: str = None,
        settings: dict = None,
    ):
        try:
            client = HiddifyClient(base_url=url, admin_key=username)
            sub_url = await client.add_client(chat_id=chat_id, user_data=settings)
            await client.close()
            return sub_url
        except Exception as err:
            error_detail = traceback.format_exc()
            logger.info(
                f"Error creating user in HiddifyPanel for chat_id {chat_id}: {err}\nDetail:{error_detail}"
            )
