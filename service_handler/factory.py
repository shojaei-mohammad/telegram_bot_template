from service_handler.hiddify_panel import HiddifyPanel
from service_handler.xui_panel import XUIPanel
from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


class CreateUserFactory:
    """
    Factory class to create user handler instances based on the specified platform.

    This class provides a method to get the appropriate user creation handler
    for different platforms such as 'xui'. It acts as a factory, abstracting the
    instantiation of handler classes.
    """

    @staticmethod
    def get_create_user_handler(platform: str):
        """
        Retrieves the user creation handler based on the given platform.

        Args:
            platform: A string representing the platform for which the user creation
                      handler is required (e.g., 'xui').

        Returns:
            An instance of a user creation handler for the specified platform.
            If the platform is not recognized, returns None and logs the information.

        """
        if platform == "xui":
            # Return an instance of the XUIPanel for 'xui' platform
            return XUIPanel()
        elif platform == "hiddify":
            # Return an instance of the HiddifyPanel for 'hiddify' platform
            return HiddifyPanel()
        else:
            # Log the case where the platform is not recognized
            logger.info(f"The platform could not be identified, Platform: {platform}")
            return None
