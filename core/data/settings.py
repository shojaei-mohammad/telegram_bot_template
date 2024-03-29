"""
settings.py
=========

This module provides configuration settings for the Telegram bot by reading environment variables.
These environment variables include settings related to the bot itself, administrator credentials,
database connection details, and other operational parameters.

Environment Variables:
----------------------
BOT_TOKEN: The token provided by Telegram for your bot.
ADMINS: A comma-separated list of user IDs who should be treated as administrators.
MYSQL_USER: The username for the MySQL database.
MYSQL_PASSWORD: The password for the MySQL database.
MYSQL_HOST: The host address of the MySQL database (typically "localhost" or an IP address).
MYSQL_DATABASE: The name of the MySQL database that the bot should use.
... (Additional environment variables you have added below)

Usage:
------
Simply import the desired configuration variable into your module:
from config import BOT_TOKEN, ADMINS, MY_SQL, ...
"""

from environs import Env

# Initialize the environment reader.
env = Env()
env.read_env()

# Telegram bot configurations
BOT_TOKEN = env.str("BOT_TOKEN")  # Token provided by @BotFather on Telegram.
BOT_ADDRESS = env.str("BOT_ADDRESS")  # Address associated with the bot, if applicable.

# Administrative configurations
ADMINS = env.list("ADMINS")  # List of user IDs designated as administrators.

# Database configurations for MySQL
MY_SQL = {
    "user": env.str("MYSQL_USER"),
    "password": env.str("MYSQL_PASSWORD"),
    "host": env.str("MYSQL_HOST"),
    "port": env.int("MYSQL_PORT"),
    "database": env.str("MYSQL_DATABASE"),
}

# Redis database URL
REDIS_URL = env.str("REDIS_URL")

CHANNEL_LINK = env.str("CHANNEL_LINK")  # Link to the channel users are directed to.
CHANNEL_ID = env.str("CHANNEL_ID")  # ID of the channel users are directed to.

# Referral configurations
BASE_REFERRAL_LINK = env.str("BASE_REFERRAL_LINK")  # Base link for referrals.

# Support configurations
SUPPORT_USERNAME = env.str("SUPPORT_USER_NAME")  # Username of the support account.
