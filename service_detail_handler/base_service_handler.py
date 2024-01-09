from abc import abstractmethod

from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


class IServiceDetail:
    @abstractmethod
    async def show_detail(
        self,
        chat_id,
        title: str,
        subscription_url: str,
        client_name: str,
        url: str,
        username: str,
        password: str,
    ):
        raise NotImplementedError("This method should be overridden in subclasses.")
