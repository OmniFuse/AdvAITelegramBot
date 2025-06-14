import pyrogram
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Message
from config import WEBAPP_LINK
from modules.models import user_db
from modules.models.site_api import fetch_user
from modules.lang import async_translate_to_lang

async def balance_command(client: pyrogram.Client, message: Message):
    user_id = message.from_user.id
    user_lang = user_db.get_user_language(user_id)
    telegram_id = str(user_id)

    user_data = await fetch_user(telegram_id)
    if user_data:
        text = (
            "ID: {id}\n"
            "Name: {name}\n"
            "Email: {email}\n"
            "Balance: {balance}"
        ).format(**user_data)
        text = await async_translate_to_lang(text, user_lang)
        btn_text = await async_translate_to_lang("Open WebApp", user_lang)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, url=WEBAPP_LINK)]])
        await message.reply_text(text, reply_markup=keyboard)
    else:
        text = await async_translate_to_lang(
            "Account not linked. Use the button below to link your Telegram account.", user_lang
        )
        btn_text = await async_translate_to_lang("Link Account", user_lang)
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(btn_text, web_app=WebAppInfo(url=WEBAPP_LINK))]]
        )
        await message.reply_text(text, reply_markup=keyboard)
