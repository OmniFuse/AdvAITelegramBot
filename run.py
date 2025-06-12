import os
import config
import pyrogram
import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from pyrogram.enums import ChatAction, ChatType, ParseMode
from modules.user.start import start, start_inline, premium_info_page, premium_plans_callback, premium_paid_notify_callback
from modules.user.help import help
from modules.user.commands import command_inline
from modules.user.settings import settings_inline, settings_language_callback, change_voice_setting, settings_voice_inlines, settings_image_count_callback, change_image_count_callback
from modules.user.assistant import settings_assistant_callback, change_mode_setting
from modules.user.lang_settings import settings_langs_callback, change_language_setting
from modules.user.user_support import settings_support_callback, support_admins_callback, admin_panel_callback
from modules.user.dev_support import support_developers_callback
from modules.user.ai_model import ai_model_settings_panel, handle_set_text_model, handle_set_image_model, handle_ai_model_heading_click
from modules.speech import text_to_voice, voice_to_text
from modules.image.img_to_text import extract_text_res, handle_show_text_callback, handle_followup_callback
from modules.maintenance import settings_others_callback, handle_feature_toggle, handle_feature_info, maintenance_check, maintenance_message, handle_donation
from modules.group.group_settings import leave_group, invite_command
from modules.feedback_nd_rating import rate_command, handle_rate_callback
from modules.group.group_info import info_command, uinfo_settings_callback, uinfo_history_callback
from modules.models.ai_res import aires, new_chat
from modules.image.image_generation import generate_command, handle_image_feedback, start_cleanup_scheduler, handle_generate_command
from modules.image.inline_image_generation import handle_inline_query, cleanup_ongoing_generations
from modules.models.inline_ai_response import cleanup_ongoing_generations as ai_cleanup_ongoing_generations
from modules.chatlogs import channel_log, user_log, error_log
from modules.user.user_settings_panel import user_settings_panel_command, handle_user_settings_callback
from modules.speech.voice_to_text import handle_voice_message, handle_voice_toggle
from modules.admin.restart import restart_command, handle_restart_callback, check_restart_marker
import modules.models.user_db as user_db
import asyncio
import logging
import datetime
from logging.handlers import RotatingFileHandler
import json
import time
from modules.models.image_service import ImageService
from modules.user.user_bans_management import ban_user, unban_user, is_user_banned, get_banned_message, get_user_by_id_or_username
from modules.user.premium_management import add_premium_status, remove_premium_status, is_user_premium, get_premium_status_message, daily_premium_check, get_premium_benefits_message, get_all_premium_users, format_premium_users_list
import multiprocessing


# Create directories if they don't exist
if not os.path.exists("sessions"):
    os.makedirs("sessions")
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging with a single main log file
MAIN_LOG_FILE = os.path.join("logs", "bot_main.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(MAIN_LOG_FILE, maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_bot_instance(bot_token, bot_index=1):
    """Create and return a Pyrogram Client instance for a given bot token."""
    # Place all session folders inside the main 'sessions' directory
    main_sessions_dir = "sessions"
    if not os.path.exists(main_sessions_dir):
        os.makedirs(main_sessions_dir)
    session_dir = os.path.join(main_sessions_dir, f"sessions_{bot_index}")
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
    advAiBot = pyrogram.Client(
            await message.reply_text("Использование: /premium <user_id_or_username> <дней>")
                await message.reply_text("Количество дней должно быть положительным числом.")
            await message.reply_text("Неверное значение дней. Укажите целое число.")
            await message.reply_text(f"Не удалось найти пользователя: {identifier}")
            await message.reply_text(f"Пользователь {target_user.mention} (ID: {target_user.id}) получил премиум на {days} дн.")
                await client.send_message(target_user.id, f"🎉 Поздравляем! Вам выдан премиум на {days} дн.\n\nИспользуйте /benefits, чтобы посмотреть привилегии.")
            await message.reply_text(f"Не удалось выдать премиум {target_user.mention}.")
            await message.reply_text("Использование: /unpremium <user_id_or_username>")
            await message.reply_text(f"Не удалось найти пользователя: {identifier}")
            await message.reply_text(f"Премиум пользователя {target_user.mention} (ID: {target_user.id}) был отменён.")
                await client.send_message(target_user.id, "ℹ️ Ваш премиум был отменён администратором.")
            await message.reply_text(f"Пользователь {target_user.mention} не найден среди премиум-активных или не удалось снять премиум.")
            await message.reply_text("Использование: /ban <user_id_or_username> [причина]")
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "Причина не указана."
            await message.reply_text(f"Не удалось найти пользователя: {identifier}")
            await message.reply_text("Администраторы не могут быть заблокированы.")
            await message.reply_text(f"Пользователь {target_user.mention} (ID: {target_user.id}) заблокирован. Причина: {reason}")
                logger.warning(f"Не удалось уведомить пользователя {target_user.id} о бане: {e}")
            await message.reply_text(f"Не удалось заблокировать пользователя {target_user.mention}.")

            await message.reply_text("Использование: /unban <user_id_or_username>")
            await message.reply_text(f"Не удалось найти пользователя: {identifier}")
            await message.reply_text(f"Пользователь {target_user.mention} (ID: {target_user.id}) разблокирован.")
                await client.send_message(target_user.id, "🎉 Вы разблокированы и снова можете пользоваться ботом!")
            await message.reply_text(f"Пользователь {target_user.mention} не найден в списке банов или разблокировка не удалась.")
        identifier = message.command[1]
        try:
            days = int(message.command[2])
            if days <= 0:
                await message.reply_text("Number of days must be a positive integer.")
                return
        except ValueError:
            await message.reply_text("Invalid number of days. Please provide an integer.")
            return

        target_user = await get_user_by_id_or_username(client, identifier)
        if not target_user:
            await message.reply_text(f"Could not find user: {identifier}")
            return

        success = await add_premium_status(target_user.id, message.from_user.id, days)
        if success:
            await message.reply_text(f"User {target_user.mention} (ID: {target_user.id}) has been granted Premium status for {days} days.")
            await channel_log(client, message, "/premium", f"Admin {message.from_user.id} granted {days} days premium to user {target_user.id}")
            try:
                await client.send_message(target_user.id, f"🎉 Congratulations! You have been granted Premium User status for {days} days.\n\nUse /benefits to see the benefits of being a premium user.")
            except Exception as e:
                logger.warning(f"Could not notify user {target_user.id} about their premium grant: {e}")
        else:
            await message.reply_text(f"Failed to grant premium status to {target_user.mention}.")

    @advAiBot.on_message(filters.command("unpremium") & filters.user(config.ADMINS))
    async def unpremium_command_handler(client, message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /unpremium <user_id_or_username>")
            return
        identifier = message.command[1]
        target_user = await get_user_by_id_or_username(client, identifier)
        if not target_user:
            await message.reply_text(f"Could not find user: {identifier}")
            return

        success = await remove_premium_status(target_user.id, revoked_by_admin=True)
        if success:
            await message.reply_text(f"Premium status for user {target_user.mention} (ID: {target_user.id}) has been revoked.")
            await channel_log(client, message, "/unpremium", f"Admin {message.from_user.id} revoked premium from user {target_user.id}")
            try:
                await client.send_message(target_user.id, "ℹ️ Your Premium User status has been revoked by an administrator.")
            except Exception as e:
                logger.warning(f"Could not notify user {target_user.id} about their premium revocation: {e}")
        else:
            await message.reply_text(f"User {target_user.mention} was not found with active premium status or could not be unpremiumed.")

    # Daily premium check scheduler
    async def premium_check_scheduler(client):
        while True:
            logger.info("Scheduler: Starting daily premium check...")
            await daily_premium_check(client_for_notification=client)
            logger.info("Scheduler: Daily premium check finished.")
            await asyncio.sleep(24 * 60 * 60) # Sleep for 24 hours

    @advAiBot.on_message(filters.command("ban") & filters.user(config.ADMINS))
    async def ban_command_handler(client, message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /ban <user_id_or_username> [reason]")
            return
        identifier = message.command[1]
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided."
        target_user = await get_user_by_id_or_username(client, identifier)
        if not target_user:
            await message.reply_text(f"Could not find user: {identifier}")
            return
        if target_user.id in config.ADMINS:
            await message.reply_text("Admins cannot be banned.")
            return
        success = await ban_user(target_user.id, message.from_user.id, reason)
        if success:
            await message.reply_text(f"User {target_user.mention} (ID: {target_user.id}) has been banned. Reason: {reason}")
            await channel_log(client, message, "/ban", f"Admin {message.from_user.id} banned user {target_user.id}. Reason: {reason}")
            try: # Notify user if possible
                banned_msg_for_user = await get_banned_message(reason)
                await client.send_message(target_user.id, banned_msg_for_user)
            except Exception as e:
                logger.warning(f"Could not notify user {target_user.id} about their ban: {e}")
        else:
            await message.reply_text(f"Failed to ban user {target_user.mention}.")

    @advAiBot.on_message(filters.command("unban") & filters.user(config.ADMINS))
    async def unban_command_handler(client, message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /unban <user_id_or_username>")
            return
        identifier = message.command[1]
        target_user = await get_user_by_id_or_username(client, identifier)
        if not target_user:
            await message.reply_text(f"Could not find user: {identifier}")
            return
        success = await unban_user(target_user.id)
        if success:
            await message.reply_text(f"User {target_user.mention} (ID: {target_user.id}) has been unbanned.")
            await channel_log(client, message, "/unban", f"Admin {message.from_user.id} unbanned user {target_user.id}")
            try: # Notify user if possible
                await client.send_message(target_user.id, "🎉 You have been unbanned and can now use the bot again!")
            except Exception as e:
                logger.warning(f"Could not notify user {target_user.id} about their unban: {e}")
        else:
            await message.reply_text(f"User {target_user.mention} was not found in the ban list or could not be unbanned.")


    @advAiBot.on_message(filters.command("start"))
    async def start_command(bot, update):
        if await check_if_banned_and_reply(bot, update): # BAN CHECK
            return

        # Start schedulers on first command if not already running
        global cleanup_scheduler_task, ongoing_generations_cleanup_task, ai_ongoing_generations_cleanup_task, premium_scheduler_task
        if not globals().get('cleanup_scheduler_task') or cleanup_scheduler_task.done():
            cleanup_scheduler_task = asyncio.create_task(cleanup_scheduler())
            logger.info("Started image generation cleanup scheduler task")
        if not globals().get('ongoing_generations_cleanup_task') or ongoing_generations_cleanup_task.done():
            ongoing_generations_cleanup_task = asyncio.create_task(cleanup_ongoing_generations())
            logger.info("Started inline generations cleanup scheduler task")
        if not globals().get('ai_ongoing_generations_cleanup_task') or ai_ongoing_generations_cleanup_task.done():
            ai_ongoing_generations_cleanup_task = asyncio.create_task(ai_cleanup_ongoing_generations())
            logger.info("Started inline AI generations cleanup scheduler task")
        if not globals().get('premium_scheduler_task') or premium_scheduler_task.done():
            premium_scheduler_task = asyncio.create_task(premium_check_scheduler(bot)) # Pass bot client
            logger.info("Started daily premium check scheduler task")

        if not hasattr(advAiBot, "_restart_checked"):
            logger.info("Checking for restart marker on first command")
            await check_restart_marker(bot)
            setattr(advAiBot, "_restart_checked", True)
            
        bot_stats["active_users"].add(update.from_user.id)
        
        # Check for deep link parameter (e.g., /start settings or t.me/bot?start=settings)
        start_param = None
        if hasattr(update, 'text') and update.text:
            parts = update.text.split()
            if len(parts) > 1:
                start_param = parts[1].strip().lower()
        if start_param == "settings":
            from modules.user.settings import send_settings_menu_as_message
            await send_settings_menu_as_message(bot, update)
            await channel_log(bot, update, "/start?settings")
            return

        # Original start logic
        if update.chat.type == ChatType.PRIVATE:
            logger.info(f"User {update.from_user.id} started the bot in private chat")
            await start(bot, update) # This is the function from modules.user.start
        else:
            logger.info(f"User {update.from_user.id} started the bot in group chat {update.chat.id} ({update.chat.title})")
            from modules.user.group_start import group_start
            await group_start(bot, update)
        
        # Append premium status message if user is premium
        premium_message = await get_premium_status_message(update.from_user.id)
        if premium_message:
            await update.reply_text(premium_message, parse_mode=ParseMode.HTML) # Assuming HTML in premium message

        await channel_log(bot, update, "/start")

    @advAiBot.on_message(filters.command("help"))
    async def help_command(bot, update):
        if await check_if_banned_and_reply(bot, update): # BAN CHECK
            return
        logger.info(f"User {update.from_user.id} requested help")
        await help(bot, update)
        await channel_log(bot, update, "/help")


    def is_chat_text_filter():
        async def funcc(_, __, update):
            if bool(update.text):
                return not update.text.startswith("/")
            return False
        return filters.create(funcc)

    # Add a custom filter for non-command messages
    def is_not_command_filter():
        async def func(_, __, message):
            if message.text:
                return not message.text.startswith('/')
            return True  # Non-text messages are not commands
        return filters.create(func)

    # Add a custom filter for replies to bot messages
    def is_reply_to_bot_filter():
        async def func(_, __, message):
            if message.reply_to_message and message.reply_to_message.from_user:
                return message.reply_to_message.from_user.id == advAiBot.me.id
            return False
        return filters.create(func)

    @advAiBot.on_message(is_chat_text_filter() & filters.text & filters.private)
    async def handle_message(client, message):
        if await check_if_banned_and_reply(client, message): # BAN CHECK
            return
        # Check for maintenance mode
        if await maintenance_check(message.from_user.id):
            maint_msg = await maintenance_message(message.from_user.id)
            await message.reply(maint_msg)
            return
        
        bot_stats["messages_processed"] += 1
        bot_stats["active_users"].add(message.from_user.id)
        logger.info(f"Processing message from user {message.from_user.id}")
        await aires(client, message)

    @advAiBot.on_inline_query()
    async def inline_query_handler(client, inline_query):
        # For inline queries, we can't directly reply with a ban message.
        # We'll log it and prevent further processing.
        user_id = inline_query.from_user.id
        is_banned, reason = await is_user_banned(user_id)
        if is_banned:
            logger.warning(f"Banned user {user_id} attempted to use inline query. Reason: {reason}")
            await inline_query.answer([], switch_pm_text="Вы заблокированы и не можете использовать бота.", switch_pm_parameter="banned")
            return
        bot_stats["active_users"].add(inline_query.from_user.id)
        logger.info(f"Processing inline query from user {inline_query.from_user.id}: '{inline_query.query}'")
        
        # Route to appropriate handler based on query content
        await handle_inline_query(client, inline_query)

    @advAiBot.on_callback_query(filters.create(lambda _, __, query: query.data in ["announce_confirm", "announce_cancel"]))
    async def announce_callback_handler(bot, callback_query):
        user_id = callback_query.from_user.id
        if not hasattr(bot, "_announce_pending") or user_id not in bot._announce_pending:
            await callback_query.answer("Нет запланированного объявления.", show_alert=True)
            return
        if callback_query.data == "announce_cancel":
            del bot._announce_pending[user_id]
            await callback_query.edit_message_text("❌ Рассылка отменена.")
            return
        # Confirm send
        text = bot._announce_pending[user_id]
        await callback_query.edit_message_text(
            f"📣 Отправка рассылки всем пользователям...\n\n{text}",
            parse_mode=ParseMode.MARKDOWN
        )
        # Send to users with Markdown
        from modules.models import user_db
        await user_db.get_usernames_message(bot, callback_query.message, text, parse_mode=ParseMode.MARKDOWN)
        await channel_log(bot, callback_query.message, "/announce", f"Admin broadcast message to users", level="WARNING")
        del bot._announce_pending[user_id]

    @advAiBot.on_callback_query()
    async def callback_query(client, callback_query):
        if await check_if_banned_and_reply(client, callback_query): # BAN CHECK (for the user who pressed the button)
            # Note: check_if_banned_and_reply expects a message-like object for reply_text
            # We might need to adjust it or handle banned callback queries differently,
            # e.g., by just answering the callback with an alert.
            try:
                banned_msg_text = await get_banned_message((await is_user_banned(callback_query.from_user.id))[1])
                await callback_query.answer(banned_msg_text, show_alert=True)
            except: # Catch any exception during answer to prevent crash
                 await callback_query.answer("Вы заблокированы и не можете использовать бота.", show_alert=True)
            return
        try:
            # Handle restart callbacks
            if callback_query.data == "confirm_restart" or callback_query.data == "cancel_restart":
                await handle_restart_callback(client, callback_query)
                return
            
            # Handle maintenance mode toggle and feature callbacks
            if callback_query.data.startswith("toggle_") and callback_query.data.count("_") >= 2:
                await handle_feature_toggle(client, callback_query)
                return
            elif callback_query.data.startswith("feature_info_"):
                await handle_feature_info(client, callback_query)
                return
            elif callback_query.data == "admin_panel":
                from modules.user.user_support import admin_panel_callback
                await admin_panel_callback(client, callback_query)
                return
            elif callback_query.data == "support_donate":
                from modules.maintenance import handle_donation
                await handle_donation(client, callback_query)
                return
            # Advanced statistics panel
            elif callback_query.data == "admin_view_stats":
                from modules.admin import handle_stats_panel
                await handle_stats_panel(client, callback_query)
                return
            elif callback_query.data == "admin_refresh_stats":
                from modules.admin import handle_refresh_stats
                await handle_refresh_stats(client, callback_query)
                return
            elif callback_query.data == "admin_export_stats":
                from modules.admin import handle_export_stats
                await handle_export_stats(client, callback_query)
                return
            # User management panel
            elif callback_query.data == "admin_users":
                from modules.admin import handle_user_management
                await handle_user_management(client, callback_query)
                return
            elif callback_query.data.startswith("admin_users_filter_"):
                from modules.admin import handle_user_management
                # Extract filter type and page from callback data
                try:
                    parts = callback_query.data.split("_")
                    if len(parts) >= 5:  # admin_users_filter_TYPE_PAGE
                        filter_type = parts[3]
                        page = int(parts[4])
                        # Support all filter types
                        valid_filters = ["all", "recent", "active", "new", "inactive", "groups"]
                        if filter_type in valid_filters:
                            await handle_user_management(client, callback_query, page, filter_type)
                        else:
                            # Default to recent if invalid filter
                            await handle_user_management(client, callback_query, page, "recent")
                    else:
                        # Default to first page, recent filter
                        await handle_user_management(client, callback_query)
                except Exception as e:
                    logger.error(f"Error in user filter handling: {str(e)}")
                    # Default to first page, recent filter
                    await handle_user_management(client, callback_query)
                return
            # Group permissions help callback
            elif callback_query.data == "group_permissions_help":
                from modules.group.group_permissions import handle_permissions_help
                await handle_permissions_help(client, callback_query)
                return
            elif callback_query.data == "dismiss_permissions_help":
                # Just acknowledge and close the message
                await callback_query.answer("Permissions help dismissed")
                # Try to delete the message if possible
                try:
                    await client.delete_messages(
                        chat_id=callback_query.message.chat.id,
                        message_ids=callback_query.message.id
                    )
                except Exception:
                    # If can't delete, just edit to a simple confirmation
                    await callback_query.edit_message_text("✅ Thanks for reviewing the permissions info!")
                return
            elif callback_query.data == "group_start":
                # Import the group_start function from user directory
                from modules.user.group_start import group_start
                # Create a simulated message object for group_start
                simulated_message = callback_query.message
                simulated_message.from_user = callback_query.from_user
                # Call group_start with the simulated message
                await group_start(client, simulated_message)
                # Answer the callback query
                await callback_query.answer("Starting bot in this group")
                return
            elif callback_query.data == "admin_header" or callback_query.data == "features_header" or callback_query.data == "admin_tools_header":
                # Just acknowledge the click for the headers
                await callback_query.answer()
                return
            
            # Standard menu callbacks
            if callback_query.data == "help_start":
                from modules.user.help import help_inline_start
                await help_inline_start(client, callback_query)
            elif callback_query.data == "help_help" or callback_query.data == "help":
                from modules.user.help import help_inline_help
                await help_inline_help(client, callback_query)
            elif callback_query.data == "back":
                await start_inline(client, callback_query)
            elif callback_query.data == "commands_start":
                from modules.user.commands import command_inline_start
                await command_inline_start(client, callback_query)
            elif callback_query.data == "commands_help":
                from modules.user.commands import command_inline_help
                await command_inline_help(client, callback_query)
            elif callback_query.data == "settings":
                from modules.user.settings import settings_inline
                await settings_inline(client, callback_query)
            elif callback_query.data == "settings_ai_models":
                await ai_model_settings_panel(client, callback_query)
            elif callback_query.data == "settings_v":
                await settings_language_callback(client, callback_query)
            elif callback_query.data in ["settings_voice", "settings_text"]:
                await change_voice_setting(client, callback_query)
            elif callback_query.data == "settings_lans":
                await settings_langs_callback(client, callback_query)
            elif callback_query.data.startswith("language_"):
                await change_language_setting(client, callback_query)
            elif callback_query.data == "settings_voice_inlines":
                await settings_voice_inlines(client, callback_query)
            elif callback_query.data == "settings_back":
                from modules.user.settings import settings_inline
                await settings_inline(client, callback_query)
            elif callback_query.data == "settings_assistant":
                await settings_assistant_callback(client, callback_query)
            elif callback_query.data == "settings_support":
                await settings_support_callback(client, callback_query)
            elif callback_query.data == "support_developers":
                await support_developers_callback(client, callback_query)
            elif callback_query.data == "support_admins":
                await support_admins_callback(client, callback_query)
            elif callback_query.data == "settings_others":
                await settings_others_callback(client, callback_query)
            elif callback_query.data.startswith("voice_toggle_"):
                await handle_voice_toggle(client, callback_query)
            elif callback_query.data.startswith("mode_"):
                await change_mode_setting(client, callback_query)
            elif callback_query.data.startswith("show_text_"):
                await handle_show_text_callback(client, callback_query)
            elif callback_query.data.startswith("followup_"):
                await handle_followup_callback(client, callback_query)
            elif callback_query.data.startswith("rate_"):
                await handle_rate_callback(client, callback_query)
            elif callback_query.data.startswith("feedback_") or \
                 callback_query.data.startswith("img_feedback_positive_") or \
                 callback_query.data.startswith("img_feedback_negative_") or \
                 callback_query.data.startswith("img_regenerate_") or \
                 callback_query.data.startswith("img_style_"):
                await handle_image_feedback(client, callback_query)
            elif callback_query.data == "group_commands":
                # Handle group command menu
                from modules.user.group_start import handle_group_command_inline
                await handle_group_command_inline(client, callback_query)
            elif callback_query.data.startswith("group_cmd_"):
                # Handle specific group command sections
                from modules.user.group_start import handle_group_callbacks
                await handle_group_callbacks(client, callback_query)
            elif callback_query.data == "about_bot" or callback_query.data == "group_support":
                # Handle other group menu buttons
                from modules.user.group_start import handle_group_callbacks
                await handle_group_callbacks(client, callback_query)
            elif callback_query.data == "admin_view_history":
                from modules.admin.user_history import show_history_search_panel
                await show_history_search_panel(client, callback_query)
                return
            elif callback_query.data.startswith("history_user_"):
                from modules.admin.user_history import handle_history_user_selection
                user_id = int(callback_query.data.split("_")[2])
                await handle_history_user_selection(client, callback_query, user_id)
                return
            elif callback_query.data.startswith("history_page_"):
                from modules.admin.user_history import handle_history_pagination
                parts = callback_query.data.split("_")
                user_id = int(parts[2])
                page = int(parts[3])
                await handle_history_pagination(client, callback_query, user_id, page)
                return
            elif callback_query.data == "history_search":
                from modules.admin.user_history import show_history_search_panel
                await show_history_search_panel(client, callback_query)
                return
            elif callback_query.data == "history_back":
                from modules.admin.user_history import show_history_search_panel
                await show_history_search_panel(client, callback_query)
                return
            elif callback_query.data.startswith("history_download_"):
                from modules.admin.user_history import get_history_download
                user_id = int(callback_query.data.split("_")[2])
                await get_history_download(client, callback_query, user_id)
                return
            elif callback_query.data == "admin_search_user":
                from modules.admin.user_history import show_user_search_form
                await show_user_search_form(client, callback_query)
                return
            elif callback_query.data == "support":
                # Handle the support callback
                from modules.user.user_support import settings_support_callback
                await settings_support_callback(client, callback_query)
                return
            # Help menu category callbacks
            elif (callback_query.data.startswith("help_") and callback_query.data != "help"):
                from modules.user.help import handle_help_category
                await handle_help_category(client, callback_query)
                return
            # Command menu category callbacks
            elif callback_query.data.startswith("cmd_"):
                if callback_query.data.endswith("_start"):
                    from modules.user.commands import handle_command_callbacks_start
                    await handle_command_callbacks_start(client, callback_query)
                elif callback_query.data.endswith("_help"):
                    from modules.user.commands import handle_command_callbacks_help
                    await handle_command_callbacks_help(client, callback_query)
                else:
                    from modules.user.commands import handle_command_callbacks
                    await handle_command_callbacks(client, callback_query)
                return
            # Image text back button handler
            elif callback_query.data.startswith("back_to_image_"):
                # Get the user ID from the callback data
                user_id = int(callback_query.data.split("_")[3])
                # Create action buttons again
                action_markup = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("📋 Show Extracted Text", callback_data=f"show_text_{user_id}")
                    ],
                    [
                        InlineKeyboardButton("❓ Ask Follow-up", callback_data=f"followup_{user_id}")
                    ]
                ])
                # Edit message back to original prompt
                await callback_query.message.edit_text(
                    "**Need anything else with this image?**",
                    reply_markup=action_markup
                )
                return
            # Group start back button handler
            elif callback_query.data == "back_to_group_start":
                from modules.user.group_start import handle_group_callbacks
                await handle_group_callbacks(client, callback_query)
                return
            elif callback_query.data == "settings_others_refresh":
                from modules.maintenance import settings_others_refresh_callback
                await settings_others_refresh_callback(client, callback_query)
                return
            elif callback_query.data == "commands":
                from modules.user.commands import command_inline_help
                await command_inline_help(client, callback_query)
            # User settings panel callbacks
            elif callback_query.data.startswith("user_settings_"):
                await handle_user_settings_callback(client, callback_query)
                return
            elif callback_query.data.startswith("uinfo_settings_"):
                await uinfo_settings_callback(client, callback_query)
                return
            elif callback_query.data.startswith("uinfo_history_"):
                await uinfo_history_callback(client, callback_query)
                return
            # Premium flow callbacks
            elif callback_query.data == "premium_info": # This is hit when user clicks "Back to Benefits"
                await premium_info_page(client, callback_query, is_callback=True)
                return
            elif callback_query.data == "premium_plans":
                await premium_plans_callback(client, callback_query)
                return
            elif callback_query.data == "premium_paid_notify":
                await premium_paid_notify_callback(client, callback_query)
                return
            # Image generation count settings
            elif callback_query.data == "settings_image_count":
                await settings_image_count_callback(client, callback_query)
                return
            elif callback_query.data.startswith("img_count_"):
                await change_image_count_callback(client, callback_query)
                return
            # AI Model Panel Callbacks
            elif callback_query.data.startswith("set_text_model_"):
                await handle_set_text_model(client, callback_query)
                return
            elif callback_query.data.startswith("set_image_model_"):
                await handle_set_image_model(client, callback_query)
                return
            elif callback_query.data.startswith("ai_model_heading_"):
                await handle_ai_model_heading_click(client, callback_query)
                return
            else:
                # Unknown callback, just acknowledge it
                await callback_query.answer("Неизвестная команда")
            
        except Exception as e:
            logger.error(f"Error in callback query handler: {e}")
            await error_log(client, "Callback Query Error", str(e))
            try:
                await callback_query.answer("Произошла ошибка. Попробуйте позже.")
            except:
                pass


    @advAiBot.on_message(filters.voice)
    async def voice(bot, message):
        if await check_if_banned_and_reply(bot, message): # BAN CHECK
            return
        # Check for maintenance mode and voice feature toggle
        from modules.maintenance import is_feature_enabled
        if await maintenance_check(message.from_user.id) or not await is_feature_enabled("voice_features"):
            maint_msg = await maintenance_message(message.from_user.id)
            await message.reply(maint_msg)
            return
        bot_stats["voice_messages_processed"] += 1
        bot_stats["active_users"].add(message.from_user.id)
        await handle_voice_message(bot, message)

    # Register the toggle callback for voice/text mode
    @advAiBot.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("toggle_voice_")))
    async def voice_toggle_callback(client, callback_query):
        await handle_voice_toggle(client, callback_query)

    # Add a new handler for replies to bot messages in groups
    @advAiBot.on_message(is_reply_to_bot_filter() & filters.group & filters.text & is_not_command_filter())
    async def handle_reply_to_bot(bot, message):
        if await check_if_banned_and_reply(bot, message): # BAN CHECK
            return
        # Check for maintenance mode and AI response toggle
        from modules.maintenance import is_feature_enabled
        if await maintenance_check(message.from_user.id) or not await is_feature_enabled("ai_response"):
            maint_msg = await maintenance_message(message.from_user.id)
            await message.reply(maint_msg)
            return
        
        bot_stats["messages_processed"] += 1
        bot_stats["active_users"].add(message.from_user.id)
        
        logger.info(f"Processing reply to bot in group {message.chat.id} from user {message.from_user.id}")
        
        # Show typing indicator
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
        
        # Log the interaction
        await user_log(bot, message, message.text)
        
        # Process the query using the AI response function
        await aires(bot, message)

    @advAiBot.on_message(filters.command("gleave"))
    async def leave_group_command(bot, update):
        if update.from_user.id in config.ADMINS:
            logger.info(f"Admin {update.from_user.id} leaving group {update.chat.id}")
            await leave_group(bot, update)
            await channel_log(bot, update, "/gleave", f"Admin leaving group {update.chat.id if update.chat else 'unknown'}")
        else:
            logger.warning(f"Unauthorized user {update.from_user.id} attempted to use gleave command")
            await update.reply_text("⛔ У вас нет прав использовать эту команду.")
            await channel_log(bot, update, "/gleave", f"Unauthorized access attempt", level="WARNING")

    @advAiBot.on_message(filters.command("rate") & filters.private)
    async def rate_commands(bot, update):
        if await check_if_banned_and_reply(bot, update): # BAN CHECK
            return
        await rate_command(bot, update)

    @advAiBot.on_message(filters.command("invite"))
    async def invite_commands(bot, update):
        if update.from_user.id in config.ADMINS:
            logger.info(f"Admin {update.from_user.id} used invite command")
            await invite_command(bot, update)
            await channel_log(bot, update, "/invite", "Admin used invite command")
        else:
            logger.warning(f"Unauthorized user {update.from_user.id} attempted to use invite command")
            await update.reply_text("⛔ У вас нет прав использовать эту команду.")
            await channel_log(bot, update, "/invite", f"Unauthorized access attempt", level="WARNING")

    @advAiBot.on_message(filters.command("uinfo"))
    async def info_commands(bot, update):
        if update.from_user.id in config.ADMINS:
            logger.info(f"Admin {update.from_user.id} requested user info")
            await info_command(bot, update)
            await channel_log(bot, update, "/uinfo", "Admin requested user info")
        else:
            logger.warning(f"Unauthorized user {update.from_user.id} attempted to use uinfo command")
            await update.reply_text("⛔ У вас нет прав использовать эту команду.")
            await channel_log(bot, update, "/uinfo", f"Unauthorized access attempt", level="WARNING")

    # Register uinfo panel callbacks
    @advAiBot.on_callback_query(filters.create(lambda _, __, q: q.data.startswith("uinfo_settings_")))
    async def uinfo_settings_cb(client, callback_query):
        await uinfo_settings_callback(client, callback_query)

    @advAiBot.on_callback_query(filters.create(lambda _, __, q: q.data.startswith("uinfo_history_")))
    async def uinfo_history_cb(client, callback_query):
        await uinfo_history_callback(client, callback_query)

    @advAiBot.on_message(filters.text & filters.command(["ai", "ask", "say"]) & filters.group)
    async def handle_group_message(bot, update):
        if await check_if_banned_and_reply(bot, update): # BAN CHECK
            return
        # Check for maintenance mode and AI response feature
        from modules.maintenance import is_feature_enabled
        if await maintenance_check(update.from_user.id) or not await is_feature_enabled("ai_response"):
            maint_msg = await maintenance_message(update.from_user.id)
            await update.reply(maint_msg)
            return
        
        logger.info(f"Processing group command from user {update.from_user.id}")
        bot_stats["messages_processed"] += 1
        bot_stats["active_users"].add(update.from_user.id)
        
        # Show typing indicator while the AI generates a response
        await bot.send_chat_action(chat_id=update.chat.id, action=ChatAction.TYPING)
        
        # Log the interaction
        command = update.text.split()[0]
        await channel_log(bot, update, command)
        await user_log(bot, update, update.text)
        
        # Process the query using the AI response function
        await aires(bot, update)


    @advAiBot.on_message(filters.command(["newchat", "reset", "new_conversation", "clear_chat", "new"]))
    async def handle_new_chat(client, message):
        if await check_if_banned_and_reply(client, message): # BAN CHECK
            return
        bot_stats["active_users"].add(message.from_user.id)
        await new_chat(client, message)
        await channel_log(client, message, "/newchat")


    @advAiBot.on_message(filters.command(["generate", "gen", "image", "img"]))
    async def handle_generate(client, message):
        if await check_if_banned_and_reply(client, message): # BAN CHECK
            return
        # Check for maintenance mode and image generation toggle
        from modules.maintenance import is_feature_enabled
        if await maintenance_check(message.from_user.id) or not await is_feature_enabled("image_generation"):
            maint_msg = await maintenance_message(message.from_user.id)
            await message.reply(maint_msg)
            return
        
        logger.info(f"User {message.from_user.id} using image generation")
        await handle_generate_command(client, message)
        # Log the command usage
        await channel_log(client, message, f"/{message.command[0]}", "Image generation requested")

    @advAiBot.on_message(filters.photo & filters.private)
    async def handle_private_image(bot, update):
        if await check_if_banned_and_reply(bot, update): # BAN CHECK
            return
        """Handler for images in private chats"""
        # Check for maintenance mode
        if await maintenance_check(update.from_user.id):
            maint_msg = await maintenance_message(update.from_user.id)
            await update.reply(maint_msg)
            return
        
        bot_stats["active_users"].add(update.from_user.id)
        user_id = update.from_user.id
        
        logger.info(f"Processing private chat image for user {user_id}")
        
        # For private chats, process all images
        await extract_text_res(bot, update)
        
        # Log usage
        await channel_log(bot, update, "Private Image Analysis")
        logger.info(f"Image analysis for user {user_id} in private chat")

    @advAiBot.on_message(filters.photo & filters.group)
    async def handle_group_image(bot, update):
        if await check_if_banned_and_reply(bot, update): # BAN CHECK
            return
        """Handler for images in group chats"""
        if await maintenance_check(update.from_user.id):
            maint_msg = await maintenance_message(update.from_user.id)
            await update.reply(maint_msg)
            return
        bot_stats["active_users"].add(update.from_user.id)
        user_id = update.from_user.id
        logger.info(f"Group image received - Chat ID: {update.chat.id}, Title: {update.chat.title}, Caption: {update.caption}")
        if not update.caption:
            logger.info(f"Image in group {update.chat.id} ignored - no caption")
            return
        caption_lower = update.caption.lower()
        has_ai_trigger = "ai" in caption_lower or "/ai" in caption_lower
        if not has_ai_trigger:
            logger.info(f"Image in group {update.chat.id} ignored - caption doesn't contain AI trigger: {update.caption}")
            return
        # Save the image context in memory (keyed by chat_id and message_id)
        key = (update.chat.id, update.message_id)
        pending_group_images[key] = {
            "user_id": user_id,
            "photo": update.photo,
            "caption": update.caption
        }
        # Prompt user for AI response
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Да, проанализировать AI", callback_data=f"group_img_ai_yes_{update.chat.id}_{update.message_id}"),
                InlineKeyboardButton("❌ Нет", callback_data=f"group_img_ai_no_{update.chat.id}_{update.message_id}")
            ]
        ])
        await update.reply_text(
            "🤖 Нужен ли AI-ответ для этого изображения и подписи?",
            reply_markup=markup
        )
        # Log usage
        await channel_log(bot, update, "Group Image AI Prompt", "Prompted for AI response on group image")
        logger.info(f"Prompted for AI response on group image in {update.chat.id} by user {user_id}")

    @advAiBot.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("group_img_ai_yes_") or query.data.startswith("group_img_ai_no_")))
    async def handle_group_img_ai_callback(bot, callback_query):
        data = callback_query.data
        parts = data.split("_")
        action = parts[3]  # 'yes' or 'no'
        chat_id = int(parts[4])
        message_id = int(parts[5])
        key = (chat_id, message_id)
        context = pending_group_images.get(key)
        if not context:
            await callback_query.answer("Срок действия изображения истёк или не найден.", show_alert=True)
            return
        if action == "no":
            await callback_query.message.edit_text("❌ Анализ изображения отменён.")
            pending_group_images.pop(key, None)
            await callback_query.answer("Отменено.")
            return
        # If 'yes', process the image and generate AI response
        await callback_query.message.edit_text("🔍 Обрабатываю изображение и генерирую AI-ответ...")
        from modules.image.img_to_text import extract_text_from_image
        from modules.core.database import get_history_collection
        from modules.models.ai_res import get_response, DEFAULT_SYSTEM_MESSAGE
        user_id = context["user_id"]
        photo = context["photo"]
        caption = context["caption"]
        # Download the image
        try:
            if isinstance(photo, list):
                photo_obj = photo[-1]
            else:
                photo_obj = photo
            file_path = f"temp_{user_id}_{int(time.time())}.jpg"
            file = await bot.download_media(photo_obj.file_id, file_name=file_path)
            extracted_text, error = await extract_text_from_image(file)
            if error:
                await callback_query.message.edit_text(f"❌ Ошибка извлечения текста\n\n{error}")
                pending_group_images.pop(key, None)
                return
            if not extracted_text or extracted_text.strip() == "":
                await callback_query.message.edit_text("⚠️ Текст на изображении не обнаружен.")
                pending_group_images.pop(key, None)
                return
            # Combine extracted text and caption
            user_question = caption
            combined_text = f"{extracted_text}\n\n[Вопрос пользователя: {user_question}]"
            # Update user history (like in aires)
            history_collection = get_history_collection()
            user_history = history_collection.find_one({"user_id": user_id})
            if user_history and 'history' in user_history:
                history = user_history['history']
                if not isinstance(history, list):
                    history = [history]
            else:
                history = DEFAULT_SYSTEM_MESSAGE.copy()
            # Add the new user query to the history
            prompt = f"The following text was extracted from an image:\n\n{combined_text}"
            history.append({"role": "user", "content": prompt})
            ai_response = get_response(history)
            history.append({"role": "assistant", "content": ai_response})
            history_collection.update_one(
                {"user_id": user_id},
                {"$set": {"history": history}},
                upsert=True
            )
            await callback_query.message.edit_text(
                f"📝 **Анализ текста изображения**\n\n{ai_response}",
                disable_web_page_preview=True
            )
            pending_group_images.pop(key, None)
            # Clean up file
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                logger.error(f"Error removing temporary file: {e}")
            await callback_query.answer("AI-ответ готов.")
        except Exception as e:
            logger.error(f"Error processing group image AI: {e}")
            await callback_query.message.edit_text(f"Ошибка обработки изображения: {str(e)}")
            pending_group_images.pop(key, None)
            await callback_query.answer("Ошибка.")

    @advAiBot.on_message(filters.command("settings"))
    async def settings_command(bot, update):
        if await check_if_banned_and_reply(bot, update): # BAN CHECK
            return
        logger.info(f"User {update.from_user.id} accessed settings")
        await user_settings_panel_command(bot, update)
        await channel_log(bot, update, "/settings")

    @advAiBot.on_message(filters.command("stats") & filters.user(config.ADMINS))
    async def stats_command(bot, update):
        logger.info(f"Admin {update.from_user.id} requested stats")
        stats_text = (
            "📊 **Статистика бота**\n\n"
            f"💬 Сообщений обработано: {bot_stats['messages_processed']}\n"
            f"🖼️ Сгенерировано изображений: {bot_stats['images_generated']}\n"
            f"️ Голосовых сообщений: {bot_stats['voice_messages_processed']}\n"
            f"👥 Активных пользователей: {len(bot_stats['active_users'])}\n"
        )
        await update.reply_text(stats_text)
        await channel_log(bot, update, "/stats", "Admin requested bot statistics")

    @advAiBot.on_message(filters.command(["announce", "broadcast", "acc"]))
    async def announce_command(bot, update):
        if update.from_user.id in config.ADMINS:
            try:
                text = update.text.split(" ", 1)[1]
                logger.info(f"Admin {update.from_user.id} broadcasting message: {text[:50]}...")
                # Show preview and ask for confirmation
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Подтвердить отправку", callback_data="announce_confirm"),
                        InlineKeyboardButton("❌ Отмена", callback_data="announce_cancel")
                    ]
                ])
                bold_text = f"**{text}**" if not text.strip().startswith("**") else text
                await update.reply_text(
                    f"**Предпросмотр рассылки:**\n\n{bold_text}",
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN
                )
                # Store the message in a temp dict for this admin (in-memory, simple)
                if not hasattr(bot, "_announce_pending"): bot._announce_pending = {}
                bot._announce_pending[update.from_user.id] = bold_text
            except IndexError:
                logger.warning(f"Admin {update.from_user.id} attempted announce without message")
                await update.reply_text(
                    "⚠️ Укажите текст для рассылки.\n\n"
                    "Пример: `/announce Привет всем! Мы добавили новые функции.`",
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            logger.warning(f"Unauthorized user {update.from_user.id} attempted to use announce command")
            await update.reply_text("⛔ У вас нет прав использовать эту команду.")
            await channel_log(bot, update, "/announce", f"Unauthorized access attempt", level="WARNING")

    @advAiBot.on_message(filters.command("logs") & filters.user(config.ADMINS))
    async def logs_command(bot, update):
        logger.info(f"Admin {update.from_user.id} requested logs")
        
        try:
            # Send status message
            status_msg = await update.reply_text(
                "📊 **Получение логов**\n\n"
                "Подготавливаю последние записи... Это займёт пару секунд."
            )
            
            # Get the latest 500 lines from the main log file
            if os.path.exists(MAIN_LOG_FILE):
                # Read the log file and get the last 500 lines
                with open(MAIN_LOG_FILE, 'r', encoding='utf-8') as f:
                    # Read all lines and take the last 500
                    lines = f.readlines()
                    last_lines = lines[-500:] if len(lines) > 500 else lines
                    log_content = ''.join(last_lines)
                
                # Create a temporary file with the latest logs
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_log_file = f"logs/latest_logs_{timestamp}.txt"
                
                with open(temp_log_file, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                # Send the file
                await bot.send_document(
                    chat_id=update.chat.id,
                    document=temp_log_file,
                    caption=f"📋 **Последние логи**\n\nПоказываю 500 последних записей на {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # Delete the temporary file
                try:
                    os.remove(temp_log_file)
                except Exception as e:
                    logger.error(f"Error removing temporary log file: {str(e)}")
                
                # Update status message
                await status_msg.edit_text("✅ **Логи получены**")
                
            else:
                await status_msg.edit_text("❌ Файл логов не найден. Бот, возможно, ещё не создал логи.")
            
            # Log this action
            await channel_log(bot, update, "/logs", "Admin requested latest logs")
            
        except Exception as e:
            logger.error(f"Error in logs command: {str(e)}")
            await update.reply_text(f"❌ **Ошибка**\n\nНе удалось получить логи: {str(e)}")
            
            # Log the error
            await error_log(bot, "LOGS_COMMAND", str(e), context=update.text, user_id=update.from_user.id)

    @advAiBot.on_message(filters.command(["clear_cache", "clearcache", "clear_images"]))
    async def clear_user_cache(client, message):
        if await check_if_banned_and_reply(client, message): # BAN CHECK
            return
        """Handle request to clear user's image cache"""
        user_id = message.from_user.id
        logger.info(f"User {user_id} requested to clear their image cache")
        
        # Clear the user's image cache
        success = await ImageService.clear_user_image_cache(user_id)
        
        if success:
            await message.reply_text("✅ **Ваш кэш изображений очищен**\n\nВсе сохранённые данные удалены.")
        else:
            await message.reply_text("ℹ️ **Кэш изображений не найден**\n\nУ вас нет сохранённых изображений для очистки.")
        
        await channel_log(client, message, "/clear_cache", f"User cleared their image cache")

    async def stats_alert(client, callback_query):
        """Show bot statistics in an alert popup"""
        from modules.maintenance import is_admin_user
        
        if not await is_admin_user(callback_query.from_user.id):
            await callback_query.answer("У вас нет прав просматривать статистику.", show_alert=True)
            return
        
        stats_text = (
            f"Messages: {bot_stats['messages_processed']}\n"
            f"Images: {bot_stats['images_generated']}\n"
            f"Voice: {bot_stats['voice_messages_processed']}\n"
            f"Users: {len(bot_stats['active_users'])}"
        )
        
        try:
            await callback_query.answer(stats_text, show_alert=True)
        except Exception as e:
            # If too long, try a shorter version
            if "MESSAGE_TOO_LONG" in str(e):
                short_stats = f"Msgs: {bot_stats['messages_processed']}, Users: {len(bot_stats['active_users'])}"
                await callback_query.answer(short_stats, show_alert=True)
            else:
                # Just acknowledge the callback
                await callback_query.answer("Не удалось показать статистику")
        
        # Refresh the admin panel with error handling
        try:
            from modules.maintenance import show_admin_panel
            await show_admin_panel(client, callback_query)
        except Exception as e:
            logger.error(f"Error refreshing admin panel: {str(e)}")
            # Don't re-raise as this is a non-critical refresh

    @advAiBot.on_message(filters.group & filters.command(["pin", "unpin", "promote", "demote", "ban", "warn"]))
    async def handle_group_admin_commands(bot, message):
        """Handle admin commands in groups with maintenance mode check"""
        # Check maintenance mode - exempt admins
        if await maintenance_check(message.from_user.id):
            maint_msg = await maintenance_message(message.from_user.id)
            await message.reply(maint_msg)
            return
        
        # Let normal Telegram permission system handle the actual execution
        pass

    @advAiBot.on_message(filters.command("restart") & filters.user(config.ADMINS))
    async def handle_restart_command(bot, update):
        """Handler for the restart command"""
        logger.info(f"Admin {update.from_user.id} used restart command")
        await restart_command(bot, update)
        await channel_log(bot, update, "/restart", "Admin initiated restart command")

    @advAiBot.on_message(filters.new_chat_members)
    async def handle_new_chat_members(client, message):
        """Handle when new members are added to a group, including the bot itself"""
        # Import the new_chat_members function from the group module
        from modules.group.new_group import new_chat_members
        await new_chat_members(client, message)
        
        # Log the event
        try:
            await channel_log(client, message, "new_members")
        except Exception as e:
            logger.error(f"Error logging new chat members: {e}")

    @advAiBot.on_message(filters.command("history") & filters.user(config.ADMINS))
    async def history_command(bot, update):
        """Handler for the history command to view a user's chat history"""
        logger.info(f"Admin {update.from_user.id} requested chat history")
        
        # Check if user ID is provided
        if len(update.command) != 2:
            await update.reply_text(
                "⚠️ **Использование**: `/history USER_ID`\n\n"
                "Пожалуйста, укажите ID пользователя для просмотра истории."
            )
            return
        
        try:
            # Get the target user ID
            target_user_id = int(update.command[1])
            
            # Send status message
            status_msg = await update.reply_text(
                f"🔍 **Получение истории чата**\n\n"
                f"Получаю историю пользователя {target_user_id}... Пожалуйста, подождите."
            )
            
            # Call the function to get user chat history
            from modules.admin.user_history import get_user_chat_history
            await get_user_chat_history(bot, update, target_user_id, status_msg)
            
            # Log this admin action
            await channel_log(bot, update, "/history", f"Admin requested chat history for user {target_user_id}")
            
        except ValueError:
            await update.reply_text("❌ **Ошибка**: ID пользователя должен быть целым числом.")
        except Exception as e:
            logger.error(f"Ошибка получения истории чата: {e}")
            await update.reply_text(f"❌ **Ошибка получения истории чата**: {str(e)}")
            await error_log(bot, "HISTORY_COMMAND", str(e), context=update.text, user_id=update.from_user.id)


    @advAiBot.on_message(filters.command("benefits"))
    async def benefits_command_handler(client, message):
        if await check_if_banned_and_reply(client, message): # BAN CHECK
            return
        
        user_id = message.from_user.id
        benefits_text = await get_premium_benefits_message(user_id)
        
        # Add a button to contact admin or view donation options
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Донат или обновление до премиума", url="https://t.me/techycsr")]
          
        ])
        
        await message.reply_text(
            benefits_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        await channel_log(client, message, "/benefits")

    @advAiBot.on_message(filters.command("upremium") & filters.user(config.ADMINS))
    async def upremium_command(bot, message):
        users = await get_all_premium_users()
        formatted = await format_premium_users_list(users)
        await message.reply_text(formatted, parse_mode=ParseMode.HTML)

    # IMPORTANT: Ensure this new ban check is added to all relevant message/command handlers
    async def check_if_banned_and_reply(client, update_obj): # Renamed to update_obj for clarity
        user_id = update_obj.from_user.id
        # Admins cannot be banned by the bot, so skip check for them.
        if user_id in config.ADMINS:
            return False

        is_banned, reason = await is_user_banned(user_id)
        if is_banned:
            banned_msg_text = await get_banned_message(reason)
            if hasattr(update_obj, 'message') and update_obj.message: # It's a CallbackQuery
                try:
                    await update_obj.answer(banned_msg_text, show_alert=True)
                except Exception as e: # Catch any exception during answer to prevent crash
                     logger.error(f"Error answering banned callback: {e}")
                     await update_obj.answer("Вы заблокированы и не можете использовать бота.", show_alert=True)
            elif hasattr(update_obj, 'reply_text'): # It's a Message
                await update_obj.reply_text(banned_msg_text, parse_mode=ParseMode.HTML)
            elif hasattr(update_obj, 'answer') and hasattr(update_obj, 'query'): # It's an InlineQuery
                 await update_obj.answer([], switch_pm_text="Вы заблокированы и не можете использовать бота.", switch_pm_parameter="banned_user")
            return True
        return False


    @advAiBot.on_message(filters.text & filters.private & filters.user(config.ADMINS))
    async def handle_admin_text_input(bot, message):
        """Handler for admin text input, including user ID for history search"""
        # Check if the user is awaiting user ID input for history
        from modules.core.database import get_session_collection
        session_collection = get_session_collection()
        
        try:
            # Debug logging to help trace issues
            logger.debug(f"Admin text handler received message: {message.text[:20]}...")
            
            user_session = session_collection.find_one({"user_id": message.from_user.id})
            if user_session and user_session.get("awaiting_user_id_for_history"):
                logger.info(f"Admin {message.from_user.id} providing user ID for history search: {message.text}")
                
                # Clear the session flag
                session_collection.update_one(
                    {"user_id": message.from_user.id},
                    {"$unset": {
                        "awaiting_user_id_for_history": "",
                        "message_id": ""
                    }}
                )
                
                # Try to parse the user ID
                try:
                    target_user_id = int(message.text.strip())
                    
                    # Send status message
                    status_msg = await message.reply_text(
                        f"🔍 **Получение истории чата**\n\n"
                        f"Получаю историю пользователя {target_user_id}... Пожалуйста, подождите."
                    )
                    
                    # Call the function to get user chat history
                    from modules.admin.user_history import get_user_chat_history
                    await get_user_chat_history(bot, message, target_user_id, status_msg)
                    
                    # Log this admin action
                    await channel_log(bot, message, "history_search", f"Admin searched chat history for user {target_user_id}")
                    
                except ValueError:
                    await message.reply_text("❌ **Ошибка**: ID пользователя должен быть целым числом.")
                except Exception as e:
                    logger.error(f"Ошибка получения истории чата: {e}")
                    await message.reply_text(f"❌ **Ошибка получения истории чата**: {str(e)}")
                    
                # Try to delete the original message to clean up
                try:
                    await message.delete()
                except Exception as e:
                    logger.debug(f"Could not delete message: {e}")
                    
                # Return True to indicate we've handled this message and prevent passing to regular message handler
                return
                
            # Debug message to confirm we're continuing to normal message handling
            logger.debug(f"Admin text not for history search, proceeding to normal handling")
        except Exception as e:
            logger.error(f"Error in admin text input handler: {e}")
        
        # If we reach here, it's not a special admin action, so proceed with normal message handling
        await handle_message(bot, message)


    # Example of integrating the ban check into an existing handler:
    # @advAiBot.on_message(is_chat_text_filter() & filters.text & filters.private)
    # async def handle_message(client, message):
    #     if await check_if_banned_and_reply(client, message):
    #         return 
    #     # ... rest of the handler ...

    return advAiBot


def run_bot(bot_token, bot_index=1):
    # No need to set event loop, .run() will handle it in the main thread of the process
    bot = create_bot_instance(bot_token, bot_index)
    bot.run()

if __name__ == "__main__":
    logger.info("🤖 Запуск продвинутого AI-бота...")
    print("🤖 Запуск продвинутого AI-бота...")
    print("✨ Оптимизирован для производительности и современного интерфейса")

    if config.MULTIPLE_BOTS:
        bot_tokens = config.get_bot_tokens()
        processes = []
        for idx, token in enumerate(bot_tokens, 1):
            p = multiprocessing.Process(target=run_bot, args=(token, idx), daemon=False)
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
    else:
        advAiBot = create_bot_instance(config.BOT_TOKEN)
        advAiBot.run()
