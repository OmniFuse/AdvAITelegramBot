from pyrogram import Client, filters
from config import DATABASE_URL, LOG_CHANNEL
from pymongo import MongoClient
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from modules.lang import async_translate_to_lang

# Initialize the MongoDB client
mongo_client = MongoClient(DATABASE_URL)

# Access or create the database and collection
db = mongo_client['aibotdb']
user_lang_collection = db['user_lang']
user_voice_collection = db["user_voice_setting"]
ai_mode_collection = db['ai_mode']

modes = {
    "chatbot": "Чат-Бот",
    "coder": "Разработчик",
    "professional": "Профессионал",
    "teacher": "Учитель",
    "therapist": "Терапевт",
    "assistant": "Ассистент",
    "gamer": "Геймер",
    "translator": "Переводчик"
}

languages = {
    "ru": "🇷🇺 Русский"
}

# Remove the /settings command panel logic from this file. Only keep inline/start settings logic.
# The inline panel should have a 'Back' button to return to the main menu/start, and not handle reset conversation directly.
# (No code for /settings command panel here.)