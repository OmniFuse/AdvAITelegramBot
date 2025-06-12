from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from modules.lang import async_translate_to_lang

from config import OWNER_ID


# Developer user IDs
developer_ids = {
    "CSR": OWNER_ID,      
    "Ankit": 987654321,    
    "Aarushi": 192837465,  
}

# Function to handle support_developers callback
async def support_developers_callback(client, callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Get developer information
    developer_info = """
Антон, напиши информацию о нас
"""
    
    # Translate the developer info and buttons
    translated_dev_info = await async_translate_to_lang(developer_info, user_id)
    back_btn = await async_translate_to_lang("🔙 Back", user_id)
    github_btn = await async_translate_to_lang("📁 GitHub", user_id)
    contact_btn = await async_translate_to_lang("💬 Contact", user_id)
    portfolio_btn = await async_translate_to_lang("🌐 Portfolio", user_id)
    donate_btn = await async_translate_to_lang("💰 Support Development", user_id)
    
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(donate_btn, callback_data="support_donate")
            ],
            [
                InlineKeyboardButton(back_btn, callback_data="support")
            ]
        ]
    )
    
    await callback.message.edit(
        text=translated_dev_info,
        reply_markup=keyboard,
        disable_web_page_preview=False
    )
