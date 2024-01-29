from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode

from core.utils.logger import LoggerSingleton
from loader import dp, db_utils

# Configure the logger
logger = LoggerSingleton.get_logger()


@dp.inline_handler(Text(equals="share"))
async def share_referral_link(query: types.inline_query):
    chat_id = query.from_user.id
    get_ref_query = "SELECT ReferralLink, ReferralCode FROM BotUsers WHERE ChatID = %s"
    (referral_link, discount) = await db_utils.fetch_data(
        get_ref_query, (chat_id,), fetch_one=True
    )
    referral_text = (
        "👋 سلام دوست عزیز! 😊\n"
        "🚀 من از یک فیلترشکن فوق‌العاده استفاده می‌کنم که واقعاً رضایت بخشه!\n\n"
        "🌐 سرعت بالا و بدون هیچ قطعی - تجربه اینترنتی بی‌نظیری رو برات فراهم می‌کنه.\n\n"
        "🎥 با این فیلترشکن، تجربه تماشای ویدیوهای آنلاین برات لذت‌بخش‌تر میشه.\n\n"
        "🔑 با بشکن به دنیای اینترنت آزاد وارد شو و از امکانات کسب درآمد هم بهره‌مند شو.\n\n"
        "🎁 و اینم بگم که میتونی یک اکانت رایگان تستی هم بگیری!\n\n"
        "همنیطور میتونی از کد تخفیفی که برات فرستادم استفاده کنی و تو اولین خریدت"
        "۱۰ درصد تخفیف بگیری.\n"
        f"👉 <code>{discount}</code>"
    )

    # Log the retrieved referral link
    logger.info(f"Retrieved referral link for user {chat_id}: {referral_link}")

    share_kb_markup = types.InlineKeyboardMarkup()
    share_btn = types.InlineKeyboardButton(text="🚪 وارد شو!", url=referral_link)
    share_kb_markup.add(share_btn)
    if referral_link:
        # Create InlineQueryResultArticles
        results = [
            types.InlineQueryResultArticle(
                id="1",
                title="🔗 اشتراک گذاری",
                description="👈🏻 برای ارسال لینک اینجا رو لمس کن!",
                thumb_url="https://i.postimg.cc/XqXhW38c/tooliz-logo.png",
                reply_markup=share_kb_markup,
                input_message_content=types.InputTextMessageContent(
                    referral_text, parse_mode=ParseMode.HTML
                ),
            ),
        ]

        # Answer inline query with the list of results
        await query.answer(results, cache_time=1, is_personal=True)

        # Log the response to inline query
        logger.info(f"Answered inline query for user {chat_id} with referral link")
