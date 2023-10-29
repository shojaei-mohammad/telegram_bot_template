from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from keyboards.inline.force_join import join_btn, start_registarion_btn
from loader import config, bot, dp, db_utils


class ForceChannelJoinMiddleware(BaseMiddleware):

    @staticmethod
    async def on_pre_process_message(message: types.Message, _data: dict):
        channel_id = config.CHANNEL_ID
        chat_id = message.from_user.id
        # Get user's membership status in the channel
        chat_member = await bot.get_chat_member(channel_id, chat_id)
        # Check if the chat id exists in the users table
        query = "SELECT COUNT(*) FROM Users WHERE ChatID=%s"
        user_exists = await db_utils.fetch_data(query, (chat_id,), fetch_one=True)
        # Check if the user is in the registration state
        user_state = await dp.current_state(user=chat_id).get_state()
        if user_exists[0] == 0 and chat_member.status not in [
            "member",
            "creator",
            "administrator",
        ]:
            prompt_text = (
                "جهت ادامه لطفا در کانال اطلاع رسانی عضو شوید.\n\n"
                "For further proceeding, first join the channel."
            )
            await message.answer(text=prompt_text, reply_markup=join_btn)

            return False  # Continue to the next middleware/handler
        elif user_exists[0] == 0 and chat_member.status in [
            "member",
            "creator",
            "administrator",
        ]:
            if user_state is not None and user_state.startswith("Registration"):
                pass
            else:
                prompt_text = (
                    "فرایند ثبت نام را آغاز کنید.\n\n"
                    "Lets start the registration process."
                )
                await message.answer(
                    text=prompt_text, reply_markup=start_registarion_btn
                )
        elif chat_member.status not in [
            "member",
            "creator",
            "administrator",
        ]:
            prompt_text = (
                "جهت ادامه لطفا در کانال اطلاع رسانی عضو شوید.\n\n"
                "For further proceeding, first join the channel."
            )
            await message.answer(text=prompt_text, reply_markup=join_btn)

            return False  # Continue to the next middleware/handler

    @staticmethod
    async def on_pre_process_callback_query(call: types.CallbackQuery, data: dict):
        channel_id = config.CHANNEL_ID
        chat_id = call.message.chat.id
        # Get user's membership status in the channel
        chat_member = await bot.get_chat_member(channel_id, chat_id)

        if chat_member.status not in [
            "member",
            "creator",
            "administrator",
        ]:
            prompt_text = (
                "جهت ادامه لطفا در کانال اطلاع رسانی عضو شوید.\n\n"
                "For further proceeding, first join the channel."
            )
            await call.message.answer(text=prompt_text, reply_markup=join_btn)

            return False  # Continue to the next middleware/handler
