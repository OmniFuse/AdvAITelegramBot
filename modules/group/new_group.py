# Importing required libraries
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_CHANNEL as STCLOG
from modules.group.group_permissions import check_bot_permissions, update_group_stats, send_permissions_message, leave_group_if_no_permissions
import asyncio

async def new_chat_members(client, message):
    user = message.from_user
    added_members = message.new_chat_members
    chat = message.chat
    bot = await client.get_me()
    bot_id = bot.id

    for member in added_members:
        if member.id == bot_id:
            # Bot was added to a group
            nam = user.mention(user.first_name)
            user_info = f"User: {user.mention(user.first_name)}\nUsername: @{user.username}\nID: {user.id}"
            group_info = f"Group ID: `{chat.id}`"
            
            # Get the member count
            try:
                members_count = await client.get_chat_members_count(chat.id)
                group_info += f"\nMembers: {members_count}"
            except Exception as e:
                print(f"Failed to get members count: {e}")

            # Send log message to admin channel
            await client.send_message(
                chat_id=STCLOG,
                text=f"**🎉#New_group! 🎉\nAdded by \n{user_info}\nGroup info\n{group_info}**",
            )
            
            # Welcome message
            message_text = (
                f"🎉 **Спасибо, {nam}, что добавили меня в группу!** 🎉\n"
            )
            message_text += """
🤖 Я здесь, чтобы помочь вашему сообществу:

• 💬 Умные беседы
• 🖼️ Генерация изображений
• 🎙️ Распознавание голоса
• 📝 Анализ текста
"""

            # Add admin rights request
            message_text += """
Чтобы работать корректно, мне нужны следующие разрешения:

✅ Удаление сообщений — для чистоты чата
✅ Приглашение пользователей — для ссылок приглашения

Давайте сделаем эту группу замечательной вместе! 🚀
"""
            
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🤖 Начать работу", callback_data="group_start"),
                        InlineKeyboardButton("📚 Команды", callback_data="group_commands")
                    ],
                    [
                        InlineKeyboardButton("🔗 Поддержка", url="https://t.me/AdvAIworld")
                    ]
                ]
            )
            
            # Send the welcome message
            await client.send_message(
                chat_id=chat.id,
                text=message_text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
            # Check bot permissions in the group
            permissions = await check_bot_permissions(client, chat.id)
            
            # Update group statistics
            await update_group_stats(chat.id, permissions, user.id)
            
            # Wait a moment before checking permissions
            await asyncio.sleep(2)
            
            # Send permissions message if needed
            await send_permissions_message(client, chat.id, permissions)
            
            # Schedule a task to check and potentially leave group after a delay
            # This gives admins some time to grant permissions
            asyncio.create_task(delayed_permission_check(client, chat.id))

async def delayed_permission_check(client, chat_id, delay_seconds=300):
    """
    Check permissions after a delay and leave if required permissions are missing
    
    Args:
        client: Telegram client
        chat_id: Chat ID to check
        delay_seconds: Delay before checking (default: 5 minutes)
    """
    try:
        # Wait for the specified delay
        await asyncio.sleep(delay_seconds)
        
        # Check permissions and leave if necessary
        await leave_group_if_no_permissions(client, chat_id)
        
    except Exception as e:
        print(f"Error in delayed permission check: {e}")
   