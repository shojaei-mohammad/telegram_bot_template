import json
from uuid import uuid4

import aiohttp

from utils.logger import LoggerSingleton

logger = LoggerSingleton.get_logger()


class XUIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
        self.session_id = None

    async def login(self, username, password):
        url = f"{self.base_url}/login"
        data = {"username": username, "password": password}
        async with self.session.post(url, data=data) as response:
            if response.status == 200:
                # Assuming the session ID is stored in a cookie
                self.session_id = response.cookies["session"].value
                return await response.json()
            else:
                raise Exception(f"Login failed with status code: {response.status}")

    async def get_inbounds(self):
        url = f"{self.base_url}/panel/api/inbounds/list"
        headers = {"Accept": "application/json", "Cookie": f"session={self.session_id}"}
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(
                    f"Failed to get inbounds with status code: {response.status}"
                )

    async def add_client(
        self,
        inbound_id,
        email,
        limit_ip=0,
        total_gb=0,
        expiry_time=0,
        enable=True,
    ):
        client_id = str(uuid4())  # Generate a unique ID for the client
        sub_id = client_id.split("-")[4]
        alter_id = client_id.split("-")[2]
        client_data = {
            "clients": [
                {
                    "id": client_id,
                    "alterId": alter_id,
                    "email": email,
                    "limitIp": limit_ip,
                    "totalGB": total_gb,
                    "expiryTime": expiry_time,
                    "enable": enable,
                    "subId": sub_id,
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
                    return subscription_url
                else:
                    raise ValueError
            else:
                raise Exception(
                    f"Failed to add client with status code: {response.status}"
                )

    async def close(self):
        await self.session.close()
