from aiogram import executor

from loader import dp
from handlers import initialize_handlers
from middlewares.throttling import ThrottlingMiddleware
from utils.notify_admins import start_up_notification, shut_down_notification
from utils.set_bot_commands import set_default_commands


async def on_startup(dispather):
    await set_default_commands(dispather)
    await start_up_notification(dispather)
    # initialize the handlers
    initialize_handlers(dispather)


async def on_shutdown(dispatcher):
    await shut_down_notification(dispatcher)


dp.middleware.setup(ThrottlingMiddleware())

print("BOT is running ...")
if __name__ == "__main__":
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
    )
