from datetime import datetime
from uuid import uuid4

import aiohttp

from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


class HiddifyClient:
    def __init__(self, base_url: str):
        self.base_url = f"{base_url}"
        self.session = None

    async def _create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            logger.info("New session created.")

    async def get_all_users(self):
        await self._create_session()
        url = f"{self.base_url}/user/"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(
                        f"Failed to get users with status code: {response.status}"
                    )
                    raise Exception(
                        f"Failed to get users with status code: {response.status}"
                    )
        except Exception as e:
            logger.error(f"Exception during get_users: {e}")
            raise

    async def get_user_detail(self, uuid):
        await self._create_session()
        url = f"{self.base_url}/user/?uuid={uuid}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(
                        f"Failed to get user by uuid with status code: {response.status}"
                    )
                    raise Exception(
                        f"Failed to get user by uuid with status code: {response.status}"
                    )
        except Exception as e:
            logger.error(f"Exception during get_user_by_uuid: {e}")
            raise

    async def add_client(self, admin_uuid, user_data):
        await self._create_session()
        client_id = str(uuid4())  # Generate a unique ID for the client
        start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url = f"{self.base_url}/{admin_uuid}/api/v1/user/"
        payload = {
            "uuid": client_id,
            "name": user_data["name"],
            "current_usage_GB": 0,
            "usage_limit_GB": int(user_data["usage_limit_GB"]),
            "package_days": user_data["package_days"],
            "start_date": start_date,
            "mode": "no_reset",
        }
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    subscription_link = (
                        f"{self.base_url}/{client_id}/#{user_data['name']}"
                    )
                    logger.info(await response.json())
                    return subscription_link

                else:
                    logger.error(
                        f"Failed to add user with status code: {response.status}"
                    )
                    raise Exception(
                        f"Failed to add user with status code: {response.status}"
                    )
        except Exception as e:
            logger.error(f"Exception during add_user: {e}")
            raise

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Session closed.")
