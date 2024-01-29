"""
loader.py
=========

This module initializes the main components required for the bot's operation:
- Establishes the database utilities for accessing the MySQL database.
- Initializes the bot instance using the token.
- Sets up the dispatcher for handling updates and handling FSM (Finite State Machine) for conversation steps.

Usage:
------
Import the desired components (e.g., `bot`, `dp`, `db_utils`) in other modules to leverage the initialized instances.

"""

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from core.data import config
from core.database import DBUtil

# Create an instance of the DBUtil class to provide utilities
# for performing operations with the MySQL database.
db_utils = DBUtil()


# Initialize the Bot instance using the token from the config module.
# This instance represents the bot and is used for sending/receiving messages.
bot = Bot(token=config.BOT_TOKEN)

# Set up the memory storage for FSM.
# FSM (Finite State Machine) storage is used to manage states in
# conversation scenarios, remembering the step and data at each state.
storage = MemoryStorage()

# Initialize the Dispatcher with the bot and memory storage instances.
# The dispatcher is responsible for dispatching updates to their appropriate handlers.
dp = Dispatcher(bot, storage=storage)
