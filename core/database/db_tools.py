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

import traceback
from typing import Optional, Union, Tuple, List, Any

import aiomysql

from core.data import settings
from core.utils.logger import LoggerSingleton

# Configure the logger
logger = LoggerSingleton.get_logger()


class DBUtil:
    _instance = None  # Private variable to store the instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:  # Corrected the 'if' condition
            cls._instance = super(DBUtil, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.host = settings.MY_SQL["host"]
            self.db_name = settings.MY_SQL["database"]
            self.db_username = settings.MY_SQL["user"]
            self.db_password = settings.MY_SQL["password"]
            self.port = settings.MY_SQL["port"]
            self.pool = None
            self.locks = {}
            self.initialized = True

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
        logger.info(f"New pool for {self.db_name} has been created.")

    async def execute_query(
        self,
        query: str,
        params: Optional[Union[Tuple, None]] = None,
        is_transaction: bool = False,
        fetch_last_insert_id: bool = False,
        batch_mode: bool = False,
        batch_params: Optional[List[Tuple]] = None,
    ) -> Union[None, int, List[int]]:
        """
        Executes the provided query using the given parameters.

        :param query: The SQL query to be executed.
        :param params: A tuple containing the parameters for the query.
        :param is_transaction: Whether the query is a part of a transaction.
        :param fetch_last_insert_id: Whether to fetch the last inserted ID.
        :param batch_mode: If True, executes multiple queries in batch.
        :param batch_params: A list of tuples containing parameters for batch execution.
        :return: None, the last inserted ID, or a list of last inserted IDs if in batch mode.
        """
        async with self.pool.acquire() as conn:
            if is_transaction or batch_mode:
                await conn.begin()
            async with conn.cursor() as cursor:
                try:
                    if batch_mode and batch_params:
                        for batch_query, batch_param in batch_params:
                            await cursor.execute(batch_query, batch_param)
                            logger.info(
                                f"Executing batch query: {batch_query} with params: {batch_param}"
                            )
                    else:
                        await cursor.execute(query, params)
                        logger.info(f"Running query: {query} with params: {params}")

                    if not is_transaction:
                        await conn.commit()

                    if fetch_last_insert_id:
                        if batch_mode:
                            # If batch_mode is True, this might need to be adjusted based on your logic
                            return [
                                cursor.lastrowid for _ in batch_params
                            ]  # List of IDs
                        return cursor.lastrowid  # Single ID

                except Exception as e:
                    logger.error(
                        f"An error occurred while executing the query: {e}\n{traceback.format_exc()}"
                    )
                    if is_transaction or batch_mode:
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

    async def check_user_exists(self, chat_id: int) -> bool:
        """
        Checks whether a user exists in the BotUsers table based on the chat ID.

        This function performs a database query to check if there's an entry
        for the given chat ID in the BotUsers table. It returns True if the user
        exists, otherwise False.

        Args:
            chat_id (int): The unique chat ID of the Telegram user.

        Returns:
            bool: True if the user exists in the BotUsers table, False otherwise.
        """
        try:
            # Query to check if the user exists in the BotUsers table
            query = "SELECT COUNT(*) FROM BotUsers WHERE ChatID = %s"
            params = (chat_id,)

            # Execute the query
            (count,) = await self.fetch_data(query, params, fetch_one=True)

            # If the count is greater than 0, user exists
            return count > 0

        except Exception as err:
            # Log any exceptions that occur
            logger.error(f"Error checking user existence for ChatID {chat_id}: {err}")
            # Re-raise the exception for further handling, or return False
            raise err

    # Store Message ID
    async def store_message_id(self, chat_id: int, message_id: int) -> None:
        """
        Stores the message ID in both Redis and MySQL.
        """
        # Lazy import to avoid circular dependency
        from core.database.redis_tools import set_shared_data

        # Store in Redis
        await set_shared_data(chat_id, "last_message_id", message_id, persistent=True)

        # Store in MySQL
        query = """
            INSERT INTO MessageIds (ChatId, MessageId)
            VALUES (%s, %s) AS new
            ON DUPLICATE KEY UPDATE MessageId = new.MessageId
        """
        await self.execute_query(query, (chat_id, message_id))

    async def get_last_message_id(self, chat_id: int) -> Optional[int]:
        """
        Retrieves the last message ID from Redis, falling back to MySQL if necessary.
        """
        # Lazy import to avoid circular dependency
        from core.database.redis_tools import get_shared_data, set_shared_data

        # Check Redis first
        message_id = await get_shared_data(chat_id, "last_message_id")
        if message_id:
            logger.info("Used redis cashe to retrive last message id")
            return message_id

        # Fetch from MySQL if not in Redis
        query = "SELECT MessageId FROM MessageIds WHERE ChatId = %s"
        result = await self.fetch_data(query, (chat_id,), fetch_one=True)

        if result:
            # Update Redis cache
            await set_shared_data(
                chat_id, "last_message_id", result[0], persistent=True
            )
            logger.info(
                "Could not find the last message ID in Redis cache. Fetched and cached it."
            )

            return result[0]

        return None

    async def reset_last_message_id(self, chat_id: int) -> None:
        """
        Resets the last message ID in both Redis and MySQL.
        """
        # Lazy import to avoid circular dependency
        from core.database.redis_tools import delete_shared_data

        # Reset in Redis
        await delete_shared_data(chat_id, "last_message_id")

        # Reset in MySQL
        query = "DELETE FROM MessageIds WHERE ChatId = %s"
        await self.execute_query(query, (chat_id,))
        logger.info("Successfully reseted the last message id.")

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
