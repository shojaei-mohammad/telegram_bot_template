from utils.logger import LoggerSingleton
from utils.xui import XUIClient

from .base_panel_handler import IPanel

logger = LoggerSingleton.get_logger()


class XUIPanel(IPanel):
    """
    Handles interactions with the XUI panel.

    This class implements the IPanel interface and provides functionality
    for creating a user in the XUI panel.
    """

    async def create_user(
        self,
        chat_id,
        url: str,
        username: str = None,
        password: str = None,
        settings: dict = None,
    ):
        """
        Creates a user in the XUI panel.

        Args:
            chat_id: The Telegram chat ID associated with the user.
            url: The base URL of the XUI panel.
            username: The username for logging into the XUI panel.
            password: The password for logging into the XUI panel.
            settings: A dictionary containing user settings such as inbound_id, email, etc.

        Returns:
            The subscription URL after successfully creating the user.

        Raises:
            Exception: If any error occurs during the user creation process.
        """
        try:
            # Initialize the XUI client with the provided base URL
            client = XUIClient(base_url=url)

            # Add a new client with the specified settings
            sub_url = await client.add_client(
                username=username,
                password=password,
                inbound_id=settings["inbound_id"],
                email=settings["email"],
                limit_ip=settings["limit_ip"],
                total_gb=settings["total_gb"],
                expiry_time=settings["expiry_time"],
            )

            # Close the XUI client session
            await client.close()

            # Return the subscription URL
            return sub_url

        except Exception as e:
            # Log the exception
            logger.error(f"Error creating user in XUIPanel for chat_id {chat_id}: {e}")

            # Re-raise the exception to be handled by the caller
            raise
