import json
from uuid import uuid4

import aiohttp

from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


class XUIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.session_id = None
        self.is_logged_in = False

    async def _create_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            logger.info("New session created.")

    async def login(self, username, password):
        await self._create_session()
        if not self.is_logged_in:
            url = f"{self.base_url}/login"
            data = {"username": username, "password": password}

            try:
                async with self.session.post(url, data=data) as response:
                    if response.status == 200:
                        self.session_id = response.cookies["session"].value
                        self.is_logged_in = True
                        logger.info("Login successful.")
                        return await response.json()
                    else:
                        logger.error(
                            f"Login failed with status code: {response.status}"
                        )
                        raise Exception(
                            f"Login failed with status code: {response.status}"
                        )
            except Exception as e:
                logger.error(f"Exception during login: {e}")
                raise

    async def _ensure_logged_in(self, username, password):
        if not self.is_logged_in:
            await self.login(username, password)

    async def get_inbounds(self, username, password):
        await self._ensure_logged_in(username, password)
        url = f"{self.base_url}/panel/api/inbounds/list"
        headers = {"Accept": "application/json", "Cookie": f"session={self.session_id}"}

        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(
                        f"Failed to get inbounds with status code: {response.status}"
                    )
                    raise Exception(
                        f"Failed to get inbounds with status code: {response.status}"
                    )
        except Exception as e:
            logger.error(f"Exception during get_inbounds: {e}")
            raise

    async def add_client(
        self,
        chat_id,
        username,
        password,
        inbound_id,
        email,
        limit_ip=0,
        total_gb=0,
        expiry_time=0,
        enable=True,
    ):
        await self._ensure_logged_in(username, password)
        client_id = str(uuid4())  # Generate a unique ID for the client
        sub_id = client_id.split("-")[4]
        client_data = {
            "clients": [
                {
                    "id": client_id,
                    "email": email,
                    "limitIp": limit_ip,
                    "totalGB": total_gb,
                    "expiryTime": expiry_time,
                    "enable": enable,
                    "subId": sub_id,
                    "tgId": chat_id,
                    "reset": 0,
                }
            ]
        }

        url = f"{self.base_url}/panel/api/inbounds/addClient"
        subscription_url = f"https://revolution.shenorika.online:2096/sub/{sub_id}"
        headers = {"Accept": "application/json", "Cookie": f"session={self.session_id}"}
        payload = {"id": inbound_id, "settings": json.dumps(client_data)}
        async with self.session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                response_text = await response.json()
                if response_text["success"]:
                    logger.info(f"User {email} successfully created.")
                    return subscription_url, None
                else:
                    raise ValueError
            else:
                raise Exception(
                    f"Failed to add client with status code: {response.status}"
                )

    async def get_user_detail(self, username, password, client_name):
        """
        Retrieves information for a specific user identified by client_name.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            client_name (str): The name of the client whose information is to be retrieved.

        Returns:
            dict: A dictionary containing user information if successful, None otherwise.
        """

        await self._ensure_logged_in(username, password)
        url = f"{self.base_url}/panel/api/inbounds/getClientTraffics/{client_name}"
        headers = {"Accept": "application/json", "Cookie": f"session={self.session_id}"}

        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["success"]:
                        return data["obj"]
                    else:
                        logger.error(f"Failed to get user info: {data.get('msg')}")
                else:
                    logger.error(
                        f"Failed to get user info with status code: {response.status}"
                    )
                    raise Exception(
                        f"Failed to get user info with status code: {response.status}"
                    )
        except Exception as e:
            logger.error(f"Exception during get_user_info: {e}")
            raise

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Session closed.")
