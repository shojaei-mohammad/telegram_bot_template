"""
Module: `database_tools`

This module provides tools for asynchronous interactions with a MySQL database using the `aiomysql` package.
It contains a class `DBUtil` that encapsulates methods to perform various database operations such as:
- Establishing a connection pool for improved performance.
- Fetching and executing SQL queries.
- Handling database locks based on chat IDs.
- Storing and retrieving specific data like message IDs, user languages, and user accounts.
- Logging database activities and errors to a specified log file.

The module depends on configurations from the `data.config` module, logging from the `utils.logger` module,
and uses the `asyncio` library for asynchronous operations.

Dependencies:
    - asyncio: For asynchronous operations.
    - traceback: For logging detailed error information.
    - aiomysql: For asynchronous MySQL operations.
    - data.config: For database configurations.
    - utils.logger: For logging activities and errors.

Note: Before using this module, make sure the required configurations are set in the `data.config` module
and the log file path is correctly configured in the `utils.logger` module.
"""

import asyncio
import traceback
from typing import Optional, Union, Tuple, List, Any

import aiomysql

from data import config
from utils.logger import configure_logger

logger = configure_logger(f"{__name__}.log")


class DBUtil:
    def __init__(self):
        self.host = config.MY_SQL["host"]
        self.db_name = config.MY_SQL["database"]
        self.db_username = config.MY_SQL["user"]
        self.db_password = config.MY_SQL["password"]
        self.port = config.MY_SQL["port"]
        self.pool = None
        self.locks = {}

    async def get_lock(self, chat_id: int) -> asyncio.locks.Lock:
        """
        This function returns a lock for a given chat_id.
        If a lock for the chat_id does not exist, it creates a new one.

        :param chat_id: the unique identifier of the chat
        :type chat_id: int
        :return: asyncio.locks.Lock object associated with the given chat_id
        :rtype: asyncio.locks.Lock
        """

        if chat_id not in self.locks:
            self.locks[chat_id] = asyncio.Lock()
        return self.locks[chat_id]

    async def _create_pool(self) -> None:
        """
        This function creates a connection pool to the MySQL database,
        using the global settings defined at the top of the script.
        This pool allows multiple co-routines to share the same connections,
        improving the performance of your application.

        :return: None
        """

        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.db_username,
            password=self.db_password,
            db=self.db_name,
            autocommit=False,
        )

    async def execute_query(
        self,
        query: str,
        params: Optional[Union[Tuple, None]] = None,
        is_transaction: bool = False,
        fetch_last_insert_id: bool = False,
    ) -> Union[None, int]:
        """
        Executes the provided query using the given parameters.

        :param query: The SQL query to be executed
        :param params: A tuple containing the parameters for the query
        :param is_transaction: Whether the query is a part of a transaction
        :param fetch_last_insert_id: Whether to fetch the last inserted ID
        :return: None or the last inserted ID if fetch_last_insert_id is True
        """
        async with self.pool.acquire() as conn:
            # If it's a transaction, begin the transaction
            if is_transaction:
                await conn.begin()
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(query, params)
                    logger.info(f"Running query: {query} with params: {params}")

                    # If it's a transaction, commit it. If not, just commit the query.
                    if is_transaction:
                        await conn.commit()
                    else:
                        # Decide here if you want to commit every regular query.
                        # It might be better to leave this out if you run many small operations in a row.
                        await conn.commit()

                    if fetch_last_insert_id:
                        return cursor.lastrowid  # return the last inserted id
                except Exception as e:
                    logger.error(
                        f"An error occurred while executing the query: {e}\n{traceback.format_exc()}"
                    )
                    # If there's an error, rollback the transaction (or query)
                    await conn.rollback()
                    raise

    async def fetch_data(
        self,
        query: str,
        params: Optional[Union[Tuple, None]] = None,
        fetch_one: bool = False,
    ) -> Union[List[Tuple[Any, ...]], Tuple[Any, ...], None]:
        """
        This function fetches data from the MySQL database.
        The query string is parameterized with the params argument.
        If the fetch_one argument is true, it returns one row; otherwise, it returns all rows.
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    logger.info(f"Running query: {query} with params: {params}")
                    await cursor.execute(query, params)
                    if fetch_one:
                        result = await cursor.fetchone()
                    else:
                        result = await cursor.fetchall()

                    logger.info(f"Query result: {result}")
                    return result
                except Exception as e:
                    logger.error(f"An error occurred: {e}\n{traceback.format_exc()}")
                    return None

    async def store_message_id(
        self, chat_id: int, message_id: int, is_bot: bool
    ) -> None:
        """
        This function stores the message id in the database.
        """
        key = "bot_message_id" if is_bot else "user_message_id"
        query = """
            INSERT INTO MessageIds (ChatId, MessageId, KeyId)
            VALUES (%s, %s, %s) AS new
            ON DUPLICATE KEY UPDATE MessageId = new.MessageId, KeyId = new.KeyId
        """

        await self.execute_query(query, (chat_id, message_id, key))

    async def get_last_bot_message_id(self, chat_id: int) -> Optional[int]:
        """
        Given a chat id, this function fetches the last message id of the bot from the database.
        If there's no such entry, None is returned.
        """
        query = """
                SELECT MessageId FROM MessageIds
                WHERE ChatId = %s AND KeyId = 'bot_message_id'
        """
        result = await self.fetch_data(query, (chat_id,), fetch_one=True)
        return result[0] if result else None

    async def get_user_acount(self, chat_id: int) -> Optional[int]:
        """
        Given a chat id, this function fetches the user accoount from the database.
        If there's no such entry, None is returned.
        """
        query = """
                SELECT UserID FROM Users
                WHERE ChatId = %s;
        """
        result = await self.fetch_data(query, (chat_id,), fetch_one=True)
        if result and isinstance(result[0], bytes):  # Check if the result is in bytes
            return result[0].decode("utf-8")
        return result[0] if result else None

    async def initialize_database(self) -> None:
        """
        This function initializes the connection to the database.
        It attempts to create a connection pool, and logs whether it was successful.
        """
        logger.info(f"Initializing database {self.db_name}")
        try:
            await self._create_pool()
            logger.info("Database pool created")
        except Exception as e:
            logger.error(
                f"An error occurred while creating database:\nError:{e}\n{traceback.format_exc()}"
            )


__all__ = ["DBUtil"]
