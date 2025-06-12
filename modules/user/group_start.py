import pyrogram
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import Message
from pyrogram.types import CallbackQuery
from modules.lang import async_translate_to_lang, batch_translate, format_with_mention, translate_ui_element
from modules.chatlogs import channel_log
import database.user_db as user_db
from config import ADMINS
import asyncio
import logging

logger = logging.getLogger(__name__)

# Define button texts with emojis for groups
group_button_list = [
    "🛠️ Команды",
    "🤖 О боте",
    "📞 Поддержка"
]

group_welcome_text = """
🚀 **Advanced AI Bot присоединился к чату!**

**Привет, {group_name}!**

Теперь я готов помочь всем в этой группе:

• 💬 **Умные групповые разговоры**
• 🔍 **Доступ к базе знаний**
• 🖼️ **Генерация изображений**
• 🎙️ **Распознавание голоса**
• 🌐 **Перевод в реальном времени**
• 📝 **Анализ текста**

Администраторы группы могут управлять моими разрешениями и настройками, используя приведённые ниже кнопки.
"""

group_tip_text = "💡 **Совет для группы:** используйте /ai с вашим вопросом или отвечайте на мои сообщения для взаимодействия со мной.\nИли используйте /img с вашим запросом, чтобы создавать изображения!\n**Больше команд: /help.**"

LOGO = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnp4MnR0YXk3ZGNjenR6NGRoaDNkc2h2NDgxa285NnExaGM1MTZmYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/S60CrN9iMxFlyp7uM8/giphy.gif"

# Command section for groups
group_command_text = """
**🤖 Команды бота для групп 🤖

Выберите функцию ниже, чтобы увидеть подробные команды и примеры для групп.

**@AdvChatGptBot**
"""

group_ai_commands_text = """
**🧠 Команды AI-чата для групп**

**Основное взаимодействие:**
- Используйте `/ai [вопрос]`, чтобы спросить напрямую
  Пример: `/ai столица Японии?`
- Отвечайте на мои сообщения для продолжения диалога
- Также можно использовать `/ask [вопрос]` или `/say [вопрос]`

**Контекст и память:**
- Я сохраняю контекст в цепочке ответов
- Новый запрос любой командой сбросит контекст
- Групповые беседы отделены от личных

**Советы для групп:**
- Для кода я корректно форматирую блоки
- Длинные ответы разбиваю на несколько сообщений
- Админы могут настроить стиль ответов в настройках

**@AdvChatGptBot**
"""

group_image_commands_text = """
**🖼️ Генерация изображений в группах**

**Создание изображений:**
- Используйте `/generate [запрос]` или `/img [запрос]` для создания изображений
  Пример: `/img киберпанк-город ночью`
- Сгенерированные изображения видят все участники
- Используйте кнопки изображения для повторов или стилей

**Анализ изображений:**
- Отправьте изображение с упоминанием бота для извлечения текста
- Для сканирования документов добавьте "scan" в подпись
- Для анализа ответьте на изображение командой `/ai analyze this`

**Настройки изображений в группе:**
- Админы могут включать или выключать генерацию
- Доступны фильтры для подходящего контента
- Могут действовать дневные лимиты против спама

**@AdvChatGptBot**
"""

**📋 Основные команды группы**

**/start** - получить приветствие
**/help** - помощь по функциям в группе
**/settings** - настройки бота (только для админов)

**Команды админов группы:**
- `/pin` - закрепить сообщение
- `/unpin` - открепить сообщение
- `/warn` - вынести предупреждение
- Настройки группы доступны только администраторам

**@AdvChatGptBot**
"""

**⚙️ Команды администратора бота**

Эти команды доступны только администраторам бота.

**/restart** - перезапустить бота
**/stats** - статистика бота
**/gleave** - выйти из группы
**/announce** - рассылка всем пользователям/группам

**Примечание:** команды доступны только администраторам, указанным в конфигурации.

**@AdvChatGptBot**
"""

async def group_start(client, message):
    """Handle the start command in groups with a modern welcome message"""
    
    # Add the group to database if not already exists
    group_id = message.chat.id
    group_name = message.chat.title
    
    # Get admin user's info who sent the command
    user_id = message.from_user.id
    
    # Check and add user to database
    await user_db.check_and_add_user(user_id)
    if message.from_user.username:
        await user_db.check_and_add_username(user_id, message.from_user.username)
    
    # Get language for translation
    user_lang = user_db.get_user_language(user_id)
    
    # Format the welcome text with group name
    formatted_text = group_welcome_text.replace("{group_name}", group_name)
    translated_welcome = await async_translate_to_lang(formatted_text, user_lang)
    
    # Translate tip text and replace bot username
    translated_tip = await async_translate_to_lang(
        group_tip_text.replace("{bot_username}", client.me.username), 
        user_lang
    )
    
    # Translate button texts
    translated_buttons = await batch_translate(group_button_list, user_id)
    
    # Create the inline keyboard buttons with translated text (arranged in two rows)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(translated_buttons[0], callback_data="group_commands"),
         InlineKeyboardButton(translated_buttons[1], callback_data="about_bot")],
        [InlineKeyboardButton(translated_buttons[2], callback_data="group_support")]
    ])
    
    # Send the welcome message with the GIF and the keyboard
    await client.send_animation(
        chat_id=group_id,
        animation=LOGO,
        caption=translated_welcome,
        reply_markup=keyboard
    )
    
    await message.reply_text(translated_tip)
    
    # Check bot permissions and update group stats
    from modules.group.group_permissions import check_bot_permissions, update_group_stats, send_permissions_message
    
    try:
        # Check permissions
        permissions = await check_bot_permissions(client, group_id)
        
        # Update group stats
        await update_group_stats(group_id, permissions, user_id)
        
        # Send permissions message if needed
        await asyncio.sleep(1)  # Small delay to let welcome message be seen first
        await send_permissions_message(client, group_id, permissions)
        
        # Schedule permission check and potential leave after 5 minutes
        from modules.group.group_permissions import leave_group_if_no_permissions
        asyncio.create_task(delayed_permission_check(client, group_id))
    except Exception as e:
        # Log error but continue
        logger.error(f"Error checking permissions in group_start: {e}")
    
    # Log the bot being added to a group
    log_text = f"Bot started in group: {group_name} (ID: {group_id}) by user {message.from_user.mention}"
    await channel_log(client, message, "/start", log_text)

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
        
        # Import and check permissions
        from modules.group.group_permissions import leave_group_if_no_permissions
        await leave_group_if_no_permissions(client, chat_id)
        
    except Exception as e:
        logger.error(f"Error in delayed permission check: {e}")

# Content for group-specific callback handlers
group_commands_text = """
## 🛠️ **Bot Commands** for Group Chats

**Basic Commands:**
• `/start` - Show this welcome message
• `/help` - Get help with bot features
• `/settings` - Configure bot preferences

**AI Interaction:**
• Reply directly to the bot's messages
• Use `/ai [question]` for specific AI queries

**Image Generation:**
• `/generate [description]` - Create images
• `/image [idea]` - Generate visual content

**Group Administration:**
• Only group admins can change bot settings
• Configure permissions in Group Settings

**Need more help?** Use the Support button below.
"""

## ⚡ **Расширенные возможности** в группах


**Умные взаимодействия:**
• Поддержка разных языков
• Контекстные беседы
• Ответы в ветках для порядка
**Создание контента:**
• Текст в изображение с разными стилями
• Расшифровка голосовых и ответы
• Анализ документов и изображений
**Инструменты знаний:**
• Поиск в интернете
• Анализ данных и визуализация
• Объяснение кода и отладка
**Оптимизация групп:**
• Автомодерация (для админов)
• Индивидуальный стиль ответов
• Сохранение FAQ для быстрого доступа
about_bot_text = """

**Создан на базе передовых технологий:**
• GPT-4o для умных ответов
• DALL·E 3 для генерации изображений
• Whisper для распознавания голоса
• Мультимодальное понимание
**Конфиденциальность:**
• История сообщений хранится временно
• Личные беседы не используются для обучения
• Контент групп остаётся конфиденциальным
**Производительность:**
• Быстрые ответы
• Одновременная работа с несколькими беседами
• Регулярные обновления с новыми функциями
"""
**Разработчик — [Chandan Singh](https://techycsr.me)** (@techycsr)
group_settings_text = """

## ⚙️ **Настройки группы**
• Выбор языка ответов

**Владельцу/админу доступны:**

• Настройка стиля и тона
• Включение/отключение функций
• Контроль кто может использовать бота
**Скоро появится:**
• Своё приветствие
• Настройки автомодерации
• Запланированные действия
• Отчёты активности
"""
**Примечание:** менять эти параметры могут только администраторы группы.
group_support_text = """
🤖 **Информация о боте Advanced AI**

Этот универсальный ассистент умеет многое в группах:
• 🖼️ Генерация изображений с DALL‑E 3
• 🎙️ Понимание голосовых сообщений
• 📝 Распознавание текста на картинках
• 💬 Продвинутые групповые диалоги
• 🌐 Поддержка разных языков
**Разработка:** [Chandan Singh](https://techycsr.me)
**Технологии:** GPT-4o и GPT-4o-mini
**Версия:** 2.0
"""
**Нужна помощь?** Выберите вариант ниже.
async def handle_group_command_inline(client, callback):
    user_id = callback.from_user.id
    
    # Translate the command text and buttons
    texts_to_translate = [group_command_text, "🧠 AI in Groups", "🖼️ Image Commands", "📋 Main Commands", "🔙 Back"]
    translated_texts = await batch_translate(texts_to_translate, user_id)
    
    # Extract translated results
    translated_command = translated_texts[0]
    ai_btn = translated_texts[1]
    img_btn = translated_texts[2]
    main_btn = translated_texts[3]
    back_btn = translated_texts[4]
    
    # Create base keyboard
    keyboard_buttons = [
        [InlineKeyboardButton(ai_btn, callback_data="group_cmd_ai")],
        [InlineKeyboardButton(img_btn, callback_data="group_cmd_img")],
        [InlineKeyboardButton(main_btn, callback_data="group_cmd_main")]
    ]
    
    # Add admin button if user is an admin
    if user_id in ADMINS:
        admin_btn = "⚙️ Admin Commands"
        keyboard_buttons.append([InlineKeyboardButton(admin_btn, callback_data="group_cmd_admin")])
    
    # Add back button
    keyboard_buttons.append([InlineKeyboardButton(back_btn, callback_data="back_to_group_start")])
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await client.edit_message_caption(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        caption=translated_command,
        reply_markup=keyboard
    )

    await callback.answer()
    return

async def handle_group_callbacks(client, callback):
    """Handle callbacks for group-specific buttons"""
    
    user_id = callback.from_user.id
    callback_data = callback.data
    user_lang = user_db.get_user_language(user_id)
    
    # Prepare back button for all menus
    back_btn_text = "↩️ Back to Main Menu"
    translated_back = await async_translate_to_lang(back_btn_text, user_lang)
    back_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(translated_back, callback_data="back_to_group_start")
    ]])
    
    # Handle different callback types
    if callback_data == "group_commands":
        # Show commands menu
        await handle_group_command_inline(client, callback)
        
    elif callback_data == "group_cmd_ai":
        # Show AI commands for groups
        translated_text = await async_translate_to_lang(group_ai_commands_text, user_lang)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_lang)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="group_commands")]
        ])
        
        await client.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            caption=translated_text,
            reply_markup=keyboard
        )
        
    elif callback_data == "group_cmd_img":
        # Show Image commands for groups
        translated_text = await async_translate_to_lang(group_image_commands_text, user_lang)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_lang)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="group_commands")]
        ])
        
        await client.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            caption=translated_text,
            reply_markup=keyboard
        )
        
    elif callback_data == "group_cmd_main":
        # Show main commands for groups
        translated_text = await async_translate_to_lang(group_main_commands_text, user_lang)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_lang)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="group_commands")]
        ])
        
        await client.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            caption=translated_text,
            reply_markup=keyboard
        )
    
    elif callback_data == "group_cmd_admin":
        # Show admin commands (only for admins)
        if user_id in ADMINS:
            back_btn = await translate_ui_element("🔙 Back to Commands", user_lang)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(back_btn, callback_data="group_commands")]
            ])
            
            translated_text = await async_translate_to_lang(group_admin_commands_text, user_lang)
            
            await client.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.id,
                caption=translated_text,
                reply_markup=keyboard
            )
        else:
            # User is not an admin, show unauthorized message
            await callback.answer("You don't have permission to view admin commands", show_alert=True)
        
    elif callback_data == "about_bot":
        # Show information about the bot
        translated_text = await async_translate_to_lang(about_bot_text, user_lang)
        
        await client.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            caption=translated_text,
            reply_markup=back_keyboard
        )
        
    elif callback_data == "group_support":
        # Show support information similar to private chat support
        translated_support = await async_translate_to_lang(group_support_text, user_lang)
        
        # Translate button labels
        contact_btn = await async_translate_to_lang("👥 Contact Developer", user_lang)
        community_btn = await async_translate_to_lang("🌐 Community", user_lang)
        source_code_btn = await async_translate_to_lang("⌨️ Source Code", user_lang)
        back_btn = await async_translate_to_lang("🔙 Back", user_lang)
        
        # Create keyboard with support options
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(contact_btn, url="https://t.me/techycsr"),
                InlineKeyboardButton(community_btn, url="https://t.me/AdvChatGpt")
            ],
            [
                InlineKeyboardButton(source_code_btn, url="https://github.com/TechyCSR/AdvAITelegramBot")
            ],
            [
                InlineKeyboardButton(back_btn, callback_data="back_to_group_start")
            ]
        ])
        
        await client.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            caption=translated_support,
            reply_markup=keyboard
        )
        
    elif callback_data == "back_to_group_start":
        # Return to the main group welcome screen
        group_name = callback.message.chat.title
        
        # Format the welcome text with group name
        formatted_text = group_welcome_text.replace("{group_name}", group_name)
        translated_welcome = await async_translate_to_lang(formatted_text, user_lang)
        
        # Translate button texts
        translated_buttons = await batch_translate(group_button_list, user_id)
        
        # Create the inline keyboard buttons with translated text (arranged in two rows)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(translated_buttons[0], callback_data="group_commands"),
             InlineKeyboardButton(translated_buttons[1], callback_data="about_bot")],
            [InlineKeyboardButton(translated_buttons[2], callback_data="group_support")]
        ])
        
        await client.edit_message_caption(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            caption=translated_welcome,
            reply_markup=keyboard
        )
    
    # Acknowledge the callback
    await callback.answer() 

    