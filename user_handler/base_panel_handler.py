from abc import abstractmethod

from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


class IPanel:
    @abstractmethod
    async def create_user(
        self,
        chat_id,
        url: str,
        username: str,
        password: str,
        settings: dict,
    ):
        raise NotImplementedError("This method should be overridden in subclasses.")
