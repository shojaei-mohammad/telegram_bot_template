import os
import subprocess
from datetime import datetime

from core.data import settings
from core.utils.logger import LoggerSingleton
from loader import bot

logger = LoggerSingleton.get_logger()


async def backup_mysql_db():
    sql_data = settings.MY_SQL
    db_name = sql_data["database"]
    host = sql_data["host"]
    user = sql_data["user"]
    password = sql_data["password"]

    try:
        # Filename for the backup
        backup_file = f"{db_name}_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.sql"

        # Running mysqldump to create a backup
        with open(backup_file, "w") as file:
            subprocess.run(
                [
                    "mysqldump",
                    "-h",
                    host,
                    "-u",
                    user,
                    f"--password={password}",
                    db_name,
                ],
                stdout=file,
            )

        # Send the backup file to the admin's chat ID
        for chat_id in settings.ADMINS:
            await bot.send_document(
                chat_id=chat_id,
                document=open(
                    backup_file, "rb"
                ),  # Make sure to open the file in binary mode
                caption=f"Database backup: {db_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            )
            logger.info("Backup sent to admin.")

        # Optionally, delete the backup file after sending
        os.remove(backup_file)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
