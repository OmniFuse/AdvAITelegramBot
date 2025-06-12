import os
import random
import asyncio
import logging
import time
from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple, Union
import re
import hashlib
import urllib.parse

from pyrogram.types import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram import Client, filters
from pymongo import MongoClient
from config import DATABASE_URL, LOG_CHANNEL, ADMINS
from modules.maintenance import maintenance_check, maintenance_message, is_feature_enabled
from modules.user.premium_management import is_user_premium
from modules.user.ai_model import get_user_ai_models, DEFAULT_IMAGE_MODEL, IMAGE_MODELS, RESTRICTED_IMAGE_MODELS
from g4f.client import AsyncClient
from g4f.Provider import PollinationsImage
import openai
from config import OPENAI_API_KEY
from modules.core.database import db_service
from pyrogram.enums import ParseMode

# Get the logger
logger = logging.getLogger(__name__)

# MongoDB setup
mongo_client = MongoClient(DATABASE_URL)
db = mongo_client['aibotdb']

def get_user_images_collection():
    return db_service.get_collection('user_images')
def get_image_feedback_collection():
    return db_service.get_collection('image_feedback')
def get_prompt_storage_collection():
    return db_service.get_collection('prompt_storage')
def get_user_image_gen_settings_collection():
    return db_service.get_collection('user_image_gen_settings')

# In-memory prompt storage as fallback (will be cached to DB)
prompt_storage = {}

# Constants for style definitions
STYLE_DEFINITIONS = {
    "realistic": {
        "name": "Realistic",
        "description": "Photo-realistic, detailed images",
        "prompt_additions": "ultra realistic, detailed, photographic quality",
        "button_text": "🖼️ Realistic"
    },
    "artistic": {
        "name": "Artistic",
        "description": "Creative, artistic style like a painting",
        "prompt_additions": "artistic style, creative, vibrant colors, painting-like",
        "button_text": "🎨 Artistic"
    },
    "sketch": {
        "name": "Sketch",
        "description": "Hand-drawn sketch or drawing style",
        "prompt_additions": "hand-drawn sketch, pencil drawing, line art, sketched appearance",
        "button_text": "✏️ Sketch"
    },
    "cartoon": {
        "name": "Cartoon",
        "description": "Fun cartoon or animated style",
        "prompt_additions": "cartoon style, animated look, colorful, simplified features",
        "button_text": "🧸 Cartoon"
    },
    "3d": {
        "name": "3D Render",
        "description": "3D rendered style with depth and texture",
        "prompt_additions": "3D render, volumetric lighting, high detail, realistic textures, depth",
        "button_text": "🌟 3D Render"
    }
}

# ====== PROMPT STORAGE FUNCTIONS ======

def store_prompt(user_id: int, prompt: str) -> str:
    """Store a prompt and return a short hash ID for callback data
    
    Args:
        user_id: The user's ID
        prompt: The prompt to store
        
    Returns:
        A short hash ID for use in callback data
    """
    # Create a hash of the prompt and user ID
    hash_object = hashlib.md5(f"{user_id}:{prompt}".encode())
    prompt_id = hash_object.hexdigest()[:8]  # Use first 8 chars of hash
    
    # Store in memory cache
    prompt_storage[prompt_id] = prompt
    
    # Also store in database for persistence
    try:
        get_prompt_storage_collection().update_one(
            {"prompt_id": prompt_id},
            {"$set": {
                "user_id": user_id,
                "prompt": prompt,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Failed to store prompt in database: {str(e)}")
    
    return prompt_id

def get_prompt(prompt_id: str) -> Optional[str]:
    """Retrieve a prompt from storage
    
    Args:
        prompt_id: The hash ID for the prompt
        
    Returns:
        The stored prompt or None if not found
    """
    # Try memory cache first
    if prompt_id in prompt_storage:
        return prompt_storage[prompt_id]
    
    # Fall back to database
    try:
        result = get_prompt_storage_collection().find_one({"prompt_id": prompt_id})
        if result and "prompt" in result:
            # Update memory cache
            prompt_storage[prompt_id] = result["prompt"]
            return result["prompt"]
    except Exception as e:
        logger.error(f"Failed to retrieve prompt from database: {str(e)}")
    
    return None

# ====== USER STATE MANAGEMENT ======

class UserGenerationState:
    """Tracks a user's current image generation state"""
    def __init__(self, user_id: int, prompt: str):
        self.user_id = user_id
        self.prompt = prompt
        self.style = None
        self.style_msg_id = None
        self.style_msg_chat_id = None
        self.is_processing = False
        self.created_at = time.time()
        
    def is_active(self) -> bool:
        """Check if this state is still valid and not expired"""
        is_valid = time.time() - self.created_at < 600  # 10 minute expiration
        if not is_valid and self.is_processing:
            # Auto-reset expired processing states
            self.is_processing = False
            logger.info(f"Auto-reset expired processing state for user {self.user_id}")
        return is_valid
    
    def set_style(self, style: str) -> None:
        """Set the selected style"""
        if style in STYLE_DEFINITIONS:
            self.style = style
        else:
            self.style = "realistic"  # Default to realistic if invalid style
            
    def set_processing(self, is_processing: bool) -> None:
        """Set processing state"""
        if is_processing:
            # Record when we start processing
            self.created_at = time.time()
        self.is_processing = is_processing
        
    def set_style_message(self, message: Message) -> None:
        """Store reference to the style selection message"""
        if message and hasattr(message, 'id') and hasattr(message, 'chat'):
            self.style_msg_id = message.id
            self.style_msg_chat_id = message.chat.id

# Global state storage
user_states: Dict[int, UserGenerationState] = {}

# ====== CORE IMAGE GENERATION ======

async def generate_images(prompt: str, style: str, max_images: int = 1, user_id: int = None) -> Tuple[Optional[List[str]], Optional[str]]:
    logger.info(f"Starting generate_images. Prompt: '{prompt[:50]}...', Style: '{style}', Max images requested: {max_images}")
    style_info = STYLE_DEFINITIONS.get(style, STYLE_DEFINITIONS["realistic"])
    enhanced_prompt = f"{prompt}, {style_info['prompt_additions']}"
    logger.info(f"Enhanced prompt for generation: '{enhanced_prompt[:50]}...'")

    # Get user-selected model (default if not set)
    if user_id is not None:
        _, user_image_model = await get_user_ai_models(user_id)
        is_premium, _, _ = await is_user_premium(user_id)
        is_admin = user_id in ADMINS
        if not is_premium and not is_admin and user_image_model in RESTRICTED_IMAGE_MODELS:
            user_image_model = DEFAULT_IMAGE_MODEL
    else:
        user_image_model = DEFAULT_IMAGE_MODEL

    image_urls_list = []
    try:
        if OPENAI_API_KEY and user_image_model.startswith("dall-e"):
            loop = asyncio.get_event_loop()
            def run_openai():
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                return client.images.generate(
                    prompt=enhanced_prompt,
                    model=user_image_model,
                    n=max_images,
                    size="1024x1024"
                )
            response = await loop.run_in_executor(None, run_openai)
        else:
            client = AsyncClient(image_provider=PollinationsImage)
            response = await client.images.generate(
                prompt=enhanced_prompt,
                model=user_image_model,
                n=max_images,
                response_format="url",
                width=1024,
                height=1024,
                quality="standard"
            )
        if not response or not response.data:
            logger.warning(f"g4f returned no image data (empty/None response.data).")
            return None, "Failed to generate images. No images were returned by the provider. Please try a different prompt or try again later."
        for i, image_object in enumerate(response.data):
            if hasattr(image_object, 'url') and image_object.url and image_object.url.startswith("https://"):
                image_urls_list.append(image_object.url)
            else:
                logger.warning(f"Image object {i} from g4f has no valid HTTPS URL. Skipping.")
    except Exception as e_generate:
        logger.error(f"Exception with g4f image generation: {str(e_generate)}.")
        # Log the error to the log channel
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"#ImgGenError\nPrompt: `{enhanced_prompt}`\nUser ID: {user_id}\nError: {str(e_generate)}"
            )
        except Exception as log_err:
            logger.error(f"Failed to log image gen error to channel: {str(log_err)}")
        # Return a generic error for the user
        return None, "There's some issue, please try in a moment or change your prompt."

    if not image_urls_list:
        logger.warning("No image URLs were collected after all attempts.")
        return None, "Failed to generate images. No images were returned by the provider. Please try a different prompt or try again later."

    return image_urls_list, None

# ====== UI COMPONENTS ======

async def update_generation_progress(client: Client, chat_id: int, message_id: int, prompt: str, style: str, num_images: int = 1, user_id: int = None) -> None:
    """Show a dynamic progress indicator while generating images, including the user's selected model."""
    progress_stages = [
        "⏳ Analyzing your prompt...",
        "🤔 Brainstorming creative concepts...",
        "🎨 Sketching out initial designs...",
        "🖌️ Applying artistic layers & textures...",
        "✨ Refining details & adding highlights...",
        "📷 Rendering final image(s)..."
    ]
    
    style_info = STYLE_DEFINITIONS.get(style, STYLE_DEFINITIONS["realistic"])
    num_images_note = f" (for {num_images} images)" if num_images > 1 else ""
    
    # Fetch the user's selected model
    user_model = None
    if user_id is not None:
        _, user_model = await get_user_ai_models(user_id)
    else:
        user_model = DEFAULT_IMAGE_MODEL
    model_note = f"\nModel: `{user_model}`"
    
    try:
        for i, stage in enumerate(progress_stages):
            # Wait between updates
            if i > 0:
                await asyncio.sleep(2.5)
            
            await client.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"🎭 **Generating Images**\n\n"
                f"Your prompt: `{prompt}`\n\n"
                f"Style: `{style_info['name']}`{num_images_note}{model_note}\n\n"
                f"{stage}"
            )
    except asyncio.CancelledError:
        logger.info("Progress updater cancelled as generation completed")
    except Exception as e:
        logger.error(f"Error updating generation progress: {str(e)}")

# ====== HANDLERS ======

async def handle_generate_command(client: Client, message: Message) -> None:
    """
    Handle image generation commands
    
    Args:
        client: Telegram client
        message: Message with command
    """
    # Check maintenance mode and image generation feature
    if await maintenance_check(message.from_user.id) or not await is_feature_enabled("image_generation"):
        maint_msg = await maintenance_message(message.from_user.id)
        await message.reply(maint_msg)
        return
        
    if not isinstance(message, Message):
        logger.error(f"Invalid message object in handle_generate_command: {type(message)}")
        return
        
    user_id = message.from_user.id
    
    try:
        # Get the prompt from the message
        if len(message.text.split()) > 1:
            prompt = message.text.split(None, 1)[1]
        else:
            await message.reply_text(
                "🖼️ **Создание изображений**\n\n"
                "Пожалуйста, укажите запрос для генерации изображений.\n\n"
                "Пример: `/img тихий горный пейзаж`\n\n"
                "После ввода запроса вы сможете выбрать художественный стиль."
            )
            return
            
        # FORCE Reset ALL processing states for this user
        # This is more aggressive than before and should fix stuck states
        for state_user_id, state in list(user_states.items()):
            if str(state_user_id) == str(user_id):
                logger.info(f"Force resetting processing state for user {state_user_id}")
                state.set_processing(False)
                
                # If state is older than 2 minutes, remove it completely
                if time.time() - state.created_at > 120:
                    del user_states[state_user_id]
                    logger.info(f"Removed stale state for user {state_user_id}")
        
        # Now check if user still has an active generation
        # This should never happen now with our aggressive reset
        if user_id in user_states and user_states[user_id].is_processing:
            # Check if the state is really old (more than 5 minutes) and just ignore it
            if time.time() - user_states[user_id].created_at > 300:
                logger.warning(f"Ignoring extremely stale processing state for user {user_id}")
                # Create a fresh state
                user_states[user_id] = UserGenerationState(user_id, prompt)
            else:
                await message.reply_text(
                    "⏳ Я уже обрабатываю ваш предыдущий запрос на изображение. Пожалуйста, дождитесь завершения."
                )
                return
            
        # Show style selection to start the process
        await show_style_selection(client, message, prompt)
        
    except Exception as e:
        logger.error(f"Error in image generation command handler: {str(e)}")
        await message.reply_text(f"❌ **Ошибка**\n\nНе удалось обработать запрос на генерацию изображения: {str(e)}")
        # Reset user state in case of error
        if user_id in user_states:
            user_states[user_id].set_processing(False)

async def handle_feedback(client: Client, callback_query: CallbackQuery) -> None:
    """Handle feedback and regeneration callbacks"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    feedback_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        parts = data.split("_")
        
        # Log complete callback data for debugging
        logger.info(f"Feedback callback received: data={data}, user_id={user_id}, chat_id={chat_id}")
        
        # Handle different callback types
        if data.startswith("img_style_"):
            # Style selection - handled by process_style_selection
            await process_style_selection(client, callback_query)
            return
            
        elif data.startswith("img_feedback_positive_"):
            # Positive feedback
            if len(parts) < 5:
                await callback_query.answer("Неверные данные обратной связи.")
                return
                
            target_user_id = int(parts[3])
            generation_id = parts[4]
            
            await callback_query.answer("Спасибо за положительный отзыв!")
            await callback_query.message.edit_text(
                callback_query.message.text + "\n\n✅ *Feedback received: You liked the images!*",
                reply_markup=None
            )
            
            # Get user info for mention
            user_mention = f"[User {user_id}](tg://user?id={user_id})"
            
            # Log positive feedback
            try:
                await client.send_message(
                    LOG_CHANNEL,
                    f"#ImgLog #Feedback #Positive\n**User**: {user_mention}\n**Time**: {feedback_time}\n**Generation ID**: `{generation_id}`"
                )
                
                # Store in database
                get_image_feedback_collection().insert_one({
                    "generation_id": generation_id,
                    "user_id": user_id,
                    "feedback_type": "positive",
                    "timestamp": feedback_time
                })
            except Exception as e:
                logger.error(f"Failed to log positive feedback: {str(e)}")
                
        elif data.startswith("img_feedback_negative_"):
            # Negative feedback
            if len(parts) < 5:
                await callback_query.answer("Неверные данные обратной связи.")
                return
                
            target_user_id = int(parts[3])
            generation_id = parts[4]
            
            await callback_query.answer("Спасибо за отзыв. Мы постараемся стать лучше!")
            await callback_query.message.edit_text(
                callback_query.message.text + "\n\n📝 *Feedback received: We'll work to improve our image generation.*",
                reply_markup=None
            )
            
            # Get user info for mention
            user_mention = f"[User {user_id}](tg://user?id={user_id})"
            
            # Log negative feedback
            try:
                await client.send_message(
                    LOG_CHANNEL,
                    f"#ImgLog #Feedback #Negative\n**User**: {user_mention}\n**Time**: {feedback_time}\n**Generation ID**: `{generation_id}`"
                )
                
                # Store in database
                get_image_feedback_collection().insert_one({
                    "generation_id": generation_id,
                    "user_id": user_id,
                    "feedback_type": "negative",
                    "timestamp": feedback_time
                })
            except Exception as e:
                logger.error(f"Failed to log negative feedback: {str(e)}")
                
        elif data.startswith("img_regenerate_"):
            # Regeneration request
            # CRITICAL FIX: Ensure we have the correct number of parts
            if len(parts) < 4:
                logger.error(f"Invalid regenerate data: {data}, parts count: {len(parts)}")
                await callback_query.answer("Неверный формат данных для регенерации.")
                return
                
            # The user_id in the callback data is the owner of the images
            target_user_id = int(parts[2])
            prompt_id = parts[3]
            
            logger.info(f"Regenerate request: clicked_user={user_id}, target_user={target_user_id}, prompt_id={prompt_id}")
            
            # Skip user verification in group chats to allow regeneration by anyone
            # This is a temporary fix to get regeneration working
            # In private chats, still enforce the user verification
            is_private = callback_query.message.chat.type == "private"
            if is_private and user_id != target_user_id:
                await callback_query.answer("You can only regenerate your own images in private chats.")
                return
            
            # Retrieve the original prompt from storage
            prompt = get_prompt(prompt_id)
            if not prompt:
                logger.error(f"Failed to retrieve prompt with ID {prompt_id}")
                await callback_query.answer("Ошибка: исходный запрос не найден. Попробуйте создать изображение заново.")
                return
            
            # Force reset ANY processing state for this user
            for state_user_id, state in list(user_states.items()):
                if str(state_user_id) == str(user_id):
                    state.set_processing(False)
                    logger.info(f"Reset processing state for user {state_user_id}")
            
            # Check if already processing after forced reset
            if user_id in user_states and user_states[user_id].is_processing:
                await callback_query.answer("Предыдущий запрос ещё выполняется. Попробуйте чуть позже.")
                # Force reset again
                user_states[user_id].set_processing(False)
                return
                
            # Delete the feedback message
            try:
                await callback_query.message.delete()
                logger.info(f"Deleted regeneration feedback message")
            except Exception as e:
                logger.error(f"Error deleting feedback message: {e}")
                
            # Get user info for mention
            user_mention = f"[User {user_id}](tg://user?id={user_id})"
                
            # Log regeneration
            try:
                await client.send_message(
                    LOG_CHANNEL,
                    f"#ImgLog #Regenerate\n**User**: {user_mention}\n**Time**: {feedback_time}\n**Prompt**: `{prompt}`"
                )
            except Exception as e:
                logger.error(f"Failed to log regeneration: {str(e)}")
                
            # Create a fresh state - completely new to avoid any old state issues
            if user_id in user_states:
                del user_states[user_id]  # Delete existing state
            # Create new state
            user_states[user_id] = UserGenerationState(user_id, prompt)
            
            # Create style selection buttons
            keyboard = []
            row = []
            
            for i, (style_id, style_info) in enumerate(STYLE_DEFINITIONS.items()):
                button = InlineKeyboardButton(
                    style_info["button_text"], 
                    callback_data=f"img_style_{style_id}_{user_id}"
                )
                
                row.append(button)
                if len(row) == 2 or i == len(STYLE_DEFINITIONS) - 1:
                    keyboard.append(row)
                    row = []
            
            style_markup = InlineKeyboardMarkup(keyboard)
            
            # Send the style selection message in the same chat where the regeneration was requested
            style_msg = await client.send_message(
                chat_id=chat_id,
                text=f"🎭 **Выберите стиль изображения для регенерации**\n\n"
                f"Ваш запрос: `{prompt}`\n\n"
                f"Пожалуйста, выберите стиль:",
                reply_markup=style_markup
            )
            
            # Save message info in user state
            user_states[user_id].style_msg_id = style_msg.id
            user_states[user_id].style_msg_chat_id = chat_id
            
            logger.info(f"Sent regeneration style selection for user {user_id} with prompt: '{prompt}'")
            
    except Exception as e:
        logger.error(f"Error handling feedback: {str(e)}")
        await callback_query.answer("Ошибка при обработке запроса.")
        # Reset ALL user states for this user in case of any error
        for state_user_id, state in list(user_states.items()):
            if str(state_user_id) == str(user_id):
                state.set_processing(False)

# ====== BACKWARD COMPATIBILITY FUNCTIONS ======

# Alias for backward compatibility with existing imports
generate_command = handle_generate_command
handle_image_feedback = handle_feedback

# Change callback data prefixes back to what's expected in run.py
async def show_style_selection(client: Client, message: Message, prompt: str) -> Message:
    """Show style selection buttons to the user"""
    user_id = message.from_user.id
    
    # Create or update the user's generation state
    user_states[user_id] = UserGenerationState(user_id, prompt)
    
    # Create style selection buttons
    keyboard = []
    row = []
    
    for i, (style_id, style_info) in enumerate(STYLE_DEFINITIONS.items()):
        button = InlineKeyboardButton(
            style_info["button_text"], 
            callback_data=f"img_style_{style_id}_{user_id}"  # Changed to match run.py expectations
        )
        
        row.append(button)
        if len(row) == 2 or i == len(STYLE_DEFINITIONS) - 1:
            keyboard.append(row)
            row = []
    
    style_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the style selection message
    style_msg = await message.reply_text(
        f"🎭 **Выберите стиль изображения**\n\n"
        f"Ваш запрос: `{prompt}`\n\n"
        f"Пожалуйста, выберите стиль:",
        reply_markup=style_markup
    )
    
    # Save message info in user state
    user_states[user_id].set_style_message(style_msg)
    
    logger.info(f"Sent style selection for user {user_id} with prompt: '{prompt}'")
    return style_msg

async def process_style_selection(client: Client, callback_query: CallbackQuery) -> None:
    """Process a style selection callback"""
    try:
        # Extract data from callback
        data = callback_query.data
        clicked_user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id  # Get the actual chat ID where the interaction is happening
        
        # Check callback format (img_style_{style}_{user_id})
        parts = data.split("_")
        if len(parts) < 4 or parts[0] != "img" or parts[1] != "style":
            await callback_query.answer("Неверный выбор. Попробуйте ещё раз.")
            return
            
        style = parts[2]  # The selected style
        target_user_id = int(parts[3])  # User this selection is for
        
        logger.info(f"Style selection: user={clicked_user_id}, style={style}, target={target_user_id}")
        
        # Only allow users to select styles for their own requests
        # For regeneration, we should always match the current user
        if clicked_user_id != target_user_id:
            logger.warning(f"User mismatch: clicked_user={clicked_user_id}, target_user={target_user_id}")
            await callback_query.answer("Это не ваш запрос на изображение.")
            return
            
        # Check if the user has an active state
        if clicked_user_id not in user_states:
            # If there's no state yet but this is a valid request from the user,
            # create a new state for them (helpful for regeneration flow)
            if callback_query.message and callback_query.message.text:
                # Try to extract prompt from the message text
                match = re.search(r"Your prompt: `(.*?)`", callback_query.message.text)
                if match:
                    prompt = match.group(1)
                    # Create a new state for this user
                    user_states[clicked_user_id] = UserGenerationState(clicked_user_id, prompt)
                    logger.info(f"Created new state for user {clicked_user_id} with prompt: {prompt}")
                else:
                    await callback_query.answer("Ваш запрос устарел. Пожалуйста, создайте новый.")
                    return
            else:
                await callback_query.answer("Ваш запрос устарел. Пожалуйста, создайте новый.")
                return
            
        # Get the user's state
        state = user_states[clicked_user_id]
        
        # Check if already processing
        if state.is_processing:
            await callback_query.answer("Изображения уже генерируются, пожалуйста, подождите...")
            return
            
        # Set state to processing to prevent duplicate requests
        state.set_processing(True)
        state.set_style(style)
        
        # Get style info
        style_info = STYLE_DEFINITIONS.get(style, STYLE_DEFINITIONS["realistic"])
        
        # Get the user's selected image model (key and display name)
        _, user_image_model = await get_user_ai_models(clicked_user_id)
        model_display_name = IMAGE_MODELS.get(user_image_model, user_image_model)
        model_note = f"\nModel: {model_display_name}"
        settings_note = "\n_You can change the model in Settings → AI Model Panel_"

        # Determine number of images to generate
        num_images_to_generate = 1 # Default for standard users
        is_premium, _, _ = await is_user_premium(clicked_user_id)
        if is_premium or clicked_user_id in ADMINS:
            user_gen_settings = get_user_image_gen_settings_collection().find_one({"user_id": clicked_user_id})
            if user_gen_settings and "generation_count" in user_gen_settings:
                num_images_to_generate = user_gen_settings["generation_count"]
            else:
                # Default for premium/admin if no setting found (can be 1 or more)
                num_images_to_generate = 1 # Or set a different default for premium, e.g., 2

        # Acknowledge the selection
        await callback_query.answer(f"Генерирую {num_images_to_generate} изображений в стиле {style_info['name']}...")
        
        processing_text_detail = (
            f"Создаю {num_images_to_generate} красивых изображений для вас!" if num_images_to_generate > 1 else "Создаю что-то особенное для вас!"
        )

        # Update the message to show processing
        processing_message = await client.edit_message_text(
            chat_id=chat_id,  # Use the actual chat ID
            message_id=callback_query.message.id,
            text=f"🎭 **Генерация изображений**\n\n"
            f"Ваш запрос: `{state.prompt}`\n\n"
            f"Стиль: `{style_info['name']}`\n\n"
            f"⏳ ИИ творит магию... {processing_text_detail}"
        )
        
        # Start the progress updater
        progress_task = asyncio.create_task(
            update_generation_progress(
                client, 
                chat_id,  # Use the actual chat ID
                processing_message.id, 
                state.prompt, 
                style,
                num_images_to_generate, # Pass num_images here
                clicked_user_id # Pass user_id for model display
            )
        )
        
        # Start the actual image generation
        await generate_and_send_images(
            client,
            processing_message,  # Pass the new processing message
            state.prompt,
            style,
            progress_task,
            callback_query.from_user,  # Pass the user object
            num_images_to_generate # Pass the number of images
        )
        
    except Exception as e:
        logger.error(f"Error processing style selection: {str(e)}")
        try:
            await callback_query.message.edit_text(
                f"❌ **Error**\n\nFailed to process style selection: {str(e)}"
            )
        except Exception:
            pass
            
        # Reset user state
        if clicked_user_id in user_states:
            user_states[clicked_user_id].set_processing(False)

def extract_valid_image_url(url: str) -> str:
    """Extract a valid HTTP/HTTPS image URL from a possibly encoded or indirect URL."""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    # Try to extract ?url=... from the string
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if 'url' in query:
        candidate = query['url'][0]
        if candidate.startswith("http://") or candidate.startswith("https://"):
            return candidate
    return None

async def generate_and_send_images(client: Client, message: Message, prompt: str, style: str, progress_task=None, user=None, num_images: int = 1) -> None:
    """Generate images and send them to the user"""
    # Get the user ID from the user object if provided, else fallback
    if user is not None:
        user_id = user.id if hasattr(user, 'id') else user.get('id', None)
    elif hasattr(message, 'from_user') and message.from_user:
        user_id = message.from_user.id
        user = message.from_user
    else:
        user_id = message.chat.id
        user = {'id': user_id}
    chat_id = message.chat.id
    generation_id = f"{user_id}_{int(time.time())}"
    generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Generate the images
        urls, error = await generate_images(prompt, style, max_images=num_images, user_id=user_id)
        
        # Cancel progress updater if it exists
        if progress_task and not progress_task.done():
            progress_task.cancel()
        
        # Handle generation errors
        if error:
            style_info = STYLE_DEFINITIONS.get(style, STYLE_DEFINITIONS["realistic"])
            await client.send_message(
                chat_id=chat_id,
                text="❌ **Не удалось сгенерировать изображение**\n\nПроизошла ошибка, попробуйте позже или измените запрос.\n\nПопробуйте другой запрос или стиль."
            )
            
            # Get user info for mention
            user_mention = get_user_mention(user)
            
            # Log the error
            try:
                await client.send_message(
                    LOG_CHANNEL,
                    f"#ImgGenError\nPrompt: `{prompt}`\nUser ID: {user_id}\nError: {error}"
                )
            except Exception as e:
                logger.error(f"Failed to log error to channel: {str(e)}")
            
            # Reset ALL processing states for this user
            for state_user_id, state in list(user_states.items()):
                if str(state_user_id) == str(user_id):
                    state.set_processing(False)
                    
            return
            
        # Delete the style/processing message
        try:
            if hasattr(message, 'id'):
                await client.delete_messages(chat_id, message.id)
        except Exception as e:
            logger.error(f"Error deleting message: {str(e)}")
        
        # Get style info
        style_info = STYLE_DEFINITIONS.get(style, STYLE_DEFINITIONS["realistic"])
        
        # Get the user's selected image model (key and display name)
        _, user_image_model = await get_user_ai_models(user_id)
        model_display_name = IMAGE_MODELS.get(user_image_model, user_image_model)
        model_note = f"\nModel: {model_display_name}"
        settings_note = "\nYou can change the model in Settings → AI Model Panel"

        # Prepare media group with generated images
        media_group = []
        for i, url in enumerate(urls):
            valid_url = extract_valid_image_url(url)
            if not valid_url:
                logger.warning(f"Skipping invalid image URL: {url}")
                continue
            if i == 0:
                caption = (
                    f"🖼️ **AI Generated Image**\n\nPrompt: `{prompt}`\nStyle: `{style_info['name']}`"
                    f"{model_note}\n\n{settings_note}"
                )
            else:
                caption = ""
            media_group.append(InputMediaPhoto(valid_url, caption=caption[:1024]))
        if not media_group:
            await client.send_message(chat_id=chat_id, text="❌ **Image Generation Failed**\n\nNo valid images were returned by the provider.")
            return
        
        # Send generated images
        sent_message = await client.send_media_group(
            chat_id=chat_id,
            media=media_group
        )
        
        # Store the prompt for potential regeneration
        prompt_id = store_prompt(user_id, prompt)
        
        # Create feedback buttons
        feedback_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👍 Love it", callback_data=f"img_feedback_positive_{user_id}_{generation_id}"),
                InlineKeyboardButton("👎 Not good", callback_data=f"img_feedback_negative_{user_id}_{generation_id}")
            ],
            [InlineKeyboardButton("🔄 Regenerate", callback_data=f"img_regenerate_{user_id}_{prompt_id}")]
        ])
        
        # Send feedback message
        feedback_msg = await client.send_message(
            chat_id=chat_id,
            text=f"**Как вам эти изображения?**\n\n**<i>Используемая модель:</i> <i>{model_display_name}</i>**\n**<i>Модель можно изменить в настройках → Панель AI моделей.</i>**\n\nВаш отзыв помогает улучшить ИИ.",
            reply_markup=feedback_markup,
            reply_to_message_id=sent_message[0].id if sent_message else None,
            parse_mode=ParseMode.DEFAULT,
            disable_web_page_preview=True
        )
        
        # Store metadata in database
        try:
            get_user_images_collection().insert_one({
                "generation_id": generation_id,
                "user_id": user_id,
                "prompt": prompt,
                "style": style,
                "timestamp": generation_time,
                "image_count": len(urls),
                "chat_id": chat_id  # Store chat_id for better tracking
            })
        except Exception as e:
            logger.error(f"Failed to store image metadata: {str(e)}")
        
        # Get user info for mention
        user_mention = get_user_mention(user)
        
        # Log to channel
        try:
            # Send images to log channel
            await client.send_media_group(LOG_CHANNEL, media_group)
            
            # Send metadata
            await client.send_message(
                LOG_CHANNEL,
                f"#ImgLog #Generated\n**Prompt**: `{prompt}`\n**Style**: `{style_info['name']}`\n"
                f"**User**: {user_mention}\n**Time**: {generation_time}\n"
                f"**Images**: {len(urls)}\n**Generation ID**: `{generation_id}`"
            )
        except Exception as e:
            logger.error(f"Failed to log to channel: {str(e)}")
        
        # Clean up image files
        for url in urls:
            try:
                os.remove(url)
            except Exception as e:
                logger.error(f"Failed to clean up image file: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}")
        # Log the error to the log channel
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"#ImgGenError\nPrompt: `{prompt}`\nUser ID: {user_id}\nError: {str(e)}"
            )
        except Exception as log_err:
            logger.error(f"Failed to log image gen error to channel: {str(log_err)}")
        await client.send_message(
            chat_id=chat_id,
            text="❌ **Не удалось сгенерировать изображение**\n\nПроизошла ошибка, попробуйте позже или измените запрос."
        )
    finally:
        # ALWAYS reset ALL user states for this user, no matter what
        for state_user_id, state in list(user_states.items()):
            if str(state_user_id) == str(user_id):
                state.set_processing(False)
                logger.info(f"Final reset for user state {state_user_id}")
        
        # Extra safety: Remove any stale states (older than 10 minutes)
        for state_user_id in list(user_states.keys()):
            if time.time() - user_states[state_user_id].created_at > 600:
                del user_states[state_user_id]
                logger.info(f"Cleanup: removed stale state for user {state_user_id}")

# ====== CLEANUP ======

def start_cleanup_scheduler():
    """Start the background cleanup scheduler"""
    
    async def run_scheduled_cleanup():
        """Background task to regularly clean up old states"""
        logger.info("Started image generation cleanup scheduler")
        while True:
            await asyncio.sleep(3600)  # Run every hour
            
            # Clean up expired user states
            to_remove = []
            current_time = time.time()
            for user_id, state in user_states.items():
                if current_time - state.created_at > 600:  # 10 minute expiration
                    to_remove.append(user_id)
                    
            for user_id in to_remove:
                del user_states[user_id]
                
            logger.info(f"Cleaned up {len(to_remove)} expired user states")
            
    # Return the coroutine function so it can be scheduled by the bot
    return run_scheduled_cleanup

# --- Add user mention helper ---
def get_user_mention(user) -> str:
    """Return a proper Telegram mention for a user object or dict."""
    if hasattr(user, 'username') and user.username:
        return f"@{user.username}"
    elif hasattr(user, 'first_name'):
        name = user.first_name
        if hasattr(user, 'last_name') and user.last_name:
            name += f" {user.last_name}"
        return f"[{name}](tg://user?id={user.id})"
    elif isinstance(user, dict):
        if user.get('username'):
            return f"@{user['username']}"
        elif user.get('first_name'):
            name = user['first_name']
            if user.get('last_name'):
                name += f" {user['last_name']}"
            return f"[{name}](tg://user?id={user['id']})"
        else:
            return f"User {user.get('id', 'unknown')}"
    else:
        return f"User {getattr(user, 'id', 'unknown')}"



