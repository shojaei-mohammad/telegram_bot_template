"""
config.py
=========

This module provides configuration settings for the Telegram bot by reading environment variables.
These environment variables include settings related to the bot itself, administrator credentials,
and database connection details.

Environment Variables:
----------------------
BOT_TOKEN: The token provided by Telegram for your bot.
ADMINS: A comma-separated list of user IDs who should be treated as administrators.
MYSQL_USER: The username for the MySQL database.
MYSQL_PASSWORD: The password for the MySQL database.
MYSQL_HOST: The host address of the MySQL database (typically "localhost" or an IP address).
MYSQL_DATABASE: The name of the MySQL database that the bot should use.

Usage:
------
Simply import the desired configuration variable into your module:
from config import BOT_TOKEN, ADMINS, MY_SQL
"""

from environs import Env

# Initialize the environment reader.
env = Env()
env.read_env()

# Telegram bot token provided by @BotFather on Telegram.
BOT_TOKEN = env.str("BOT_TOKEN")

# List of user IDs that should be treated as administrators.
# These users might have special privileges or receive notifications.
ADMINS = env.list("ADMINS")

# MySQL database configuration.
MY_SQL = {
    'user': env.str("MYSQL_USER"),  # MySQL database username.
    'password': env.str("MYSQL_PASSWORD"),  # MySQL database password.
    'host': env.str("MYSQL_HOST"),  # Host address for the MySQL server.
    'database': env.str("MYSQL_DATABASE"),  # Name of the database to be used.
}
