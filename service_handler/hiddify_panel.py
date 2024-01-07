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
            client = HiddifyClient(base_url=url)
            sub_url = await client.add_client(admin_uuid=username, user_data=settings)
            return sub_url
        except Exception as err:
            error_detail = traceback.format_exc()
            logger.info(
                f"An error occuraed during hiddify user creation.Error:{err}\nDetails:{error_detail}"
            )
