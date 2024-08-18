from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from jwt_ import create_jwt, verify_jwt
from config import DATABASE_URL

# Initialize the MongoDB client
mongo_client = MongoClient(DATABASE_URL)

# Access or create the database and collection
db = mongo_client['aibotdb']
ai_mode_collection = db['ai_mode']

# Dictionary of modes with labels
modes = {
    "chatbot": "Chatbot",
    "coder": "Coder/Developer",
    "professional": "Professional",
    "teacher": "Teacher",
    "therapist": "Therapist",
    "assistant": "Personal Assistant",
    "gamer": "Gamer",
    "translator": "Translator"
}
def authenticate_user(user_id, token):
    # Verifies JWT and checks the user in the database
    user = verify_jwt(token)
    if user and user['user_id'] == user_id:
        return True
    return False
# Function to handle settings assistant callback
async def settings_assistant_callback(client, callback):
    user_id = callback.from_user.id
    
    # Authenticate user
    token = callback.from_user.auth_token  # Assuming token is passed with callback (Modify accordingly)
    if not authenticate_user(user_id, token):
        await callback.message.reply("Authentication failed. Please log in again.")
        return

    # Fetch the user's current mode from the database
    user_mode_doc = ai_mode_collection.find_one({"user_id": user_id})
    if user_mode_doc:
        current_mode = user_mode_doc['mode']
    else:
        current_mode = "chatbot"
        ai_mode_collection.insert_one({"user_id": user_id, "mode": current_mode})
    
    current_mode_label = modes[current_mode]
    message_text = f"Current mode: {current_mode_label}"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🤖 Chatbot", callback_data="mode_chatbot"),
                InlineKeyboardButton("💻 Coder/Developer", callback_data="mode_coder")
            ],
            [
                InlineKeyboardButton("👔 Professional", callback_data="mode_professional"),
                InlineKeyboardButton("📚 Teacher", callback_data="mode_teacher")
            ],
            [
                InlineKeyboardButton("🩺 Therapist", callback_data="mode_therapist"),
                InlineKeyboardButton("📝 Assistant", callback_data="mode_assistant")
            ],
            [
                InlineKeyboardButton("🎮 Gamer", callback_data="mode_gamer"),
                InlineKeyboardButton("🌐 Translator", callback_data="mode_translator")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="settings_back")
            ]
        ]
    )

    await callback.message.edit(
        text=message_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# Function to handle mode setting change
async def change_mode_setting(client, callback):
    mode = callback.data.split("_")[1]
    user_id = callback.from_user.id

    # Authenticate user
    token = callback.from_user.auth_token  # Assuming token is passed with callback (Modify accordingly)
    if not authenticate_user(user_id, token):
        await callback.message.reply("Authentication failed. Please log in again.")
        return

    # Update the user's mode in the database
    ai_mode_collection.update_one(
        {"user_id": user_id},
        {"$set": {"mode": mode}},
        upsert=True
    )

    current_mode_label = modes[mode]
    message_text = f"Current mode: {current_mode_label}"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🤖 Chatbot", callback_data="mode_chatbot"),
                InlineKeyboardButton("💻 Coder/Developer", callback_data="mode_coder")
            ],
            [
                InlineKeyboardButton("👔 Professional", callback_data="mode_professional"),
                InlineKeyboardButton("📚 Teacher", callback_data="mode_teacher")
            ],
            [
                InlineKeyboardButton("🩺 Therapist", callback_data="mode_therapist"),
                InlineKeyboardButton("📝 Assistant", callback_data="mode_assistant")
            ],
            [
                InlineKeyboardButton("🎮 Gamer", callback_data="mode_gamer"),
                InlineKeyboardButton("🌐 Translator", callback_data="mode_translator")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="settings_back")
            ]
        ]
    )

    await callback.message.edit(
        text=message_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
