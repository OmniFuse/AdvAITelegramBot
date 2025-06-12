import pyrogram
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import Message
from pyrogram.types import InlineQuery
from pyrogram.types import CallbackQuery
from modules.lang import async_translate_to_lang, batch_translate, translate_ui_element
from modules.chatlogs import channel_log
from config import ADMINS


command__text = """
**🤖 Команды бота 🤖**

Выберите функцию ниже, чтобы увидеть подробные команды и примеры.

**@AdvChatGptBot**
"""

ai_commands_text = """
**🧠 Команды AI-чата**

**В личных чатах:**
- Просто напишите сообщение, и я отвечу
- Отправьте голосовое сообщение, чтобы получить текстовый ответ
- Используйте `/new` или `/newchat` для начала новой беседы

**В группах:**
- Используйте `/ai [вопрос]`, чтобы спросить напрямую
  Пример: `/ai какая погода в Париже?`
- Отвечайте на мои сообщения для продолжения диалога
- В качестве альтернативы используйте `/ask [вопрос]` или `/say [вопрос]`

**Полезные советы:**
- Я помню контекст разговора в личных чатах
- Для вопросов по программированию указывайте язык для лучшего форматирования
- Используйте `/new` для очистки истории беседы

**@AdvChatGptBot**
"""

image_commands_text = """
**🖼️ Команды генерации изображений**

**В личных чатах:**
- Используйте `/generate [запрос]` или `/img [запрос]` для создания изображений
  Пример: `/img спокойный горный пейзаж на закате`
- После ввода запроса выберите художественный стиль
- Нажмите «сгенерировать снова», чтобы повторить попытку

**В группах:**
- Используйте те же команды, что и в личных чатах
- Все участники видят и могут реагировать на изображения
- Перегенерировать может только отправивший запрос

**Анализ изображений:**
- Отправьте любое изображение для извлечения и анализа текста
- Добавьте "ai" в подпись изображения для анализа в группах

**Полезные советы:**
- Чем подробнее запрос, тем лучше результат
- Пробуйте разные стили для разнообразных результатов
- Указывайте художественные референсы для нужной стилистики

**@AdvChatGptBot**
"""

main_commands_text = """
**📋 Основные команды**

**/start** - запустить бота и увидеть приветствие
**/help** - показать справку
**/settings** - настроить бота
**/rate** - оценить бота

**@AdvChatGptBot**
"""

admin_commands_text = """
**⚙️ Команды администратора бота**

Эти команды доступны только администраторам бота.

**/premium <user_id|username> <days>** - выдать премиум
**/unpremium <user_id|username>** - убрать премиум
**/upremium** - список премиум-пользователей
**/ban <user_id|username> [reason]** - заблокировать пользователя
**/unban <user_id|username>** - разблокировать пользователя
**/history <user_id>** - история чата пользователя
**/uinfo <user_id|username>** - информация о пользователе
**/announce <message>** - сообщение всем пользователям
**/logs** - последние логи бота
**/stats** - статистика бота
**/restart** - перезапустить бота
**/gleave** - выйти из текущей группы
**/invite** - получить ссылку приглашения

**Примечание:** эти команды доступны только администраторам, указанным в конфигурации.

**@AdvChatGptBot**
"""


async def command_inline(client, callback):
    user_id = callback.from_user.id
    
    # Translate the command text and buttons
    texts_to_translate = [command__text, "🧠 AI Response", "🖼️ Image Generation", "📋 Main Commands", "🔙 Back"]
    translated_texts = await batch_translate(texts_to_translate, user_id)
    
    # Extract translated results
    translated_command = translated_texts[0]
    ai_btn = translated_texts[1]
    img_btn = translated_texts[2]
    main_btn = translated_texts[3]
    back_btn = translated_texts[4]
    
    # Create base keyboard
    keyboard_buttons = [
        [InlineKeyboardButton(ai_btn, callback_data="cmd_ai")],
        [InlineKeyboardButton(img_btn, callback_data="cmd_img")],
        [InlineKeyboardButton(main_btn, callback_data="cmd_main")]
    ]
    
    # Add admin button if user is an admin
    if user_id in ADMINS:
        admin_btn = "⚙️ Admin Commands"
        keyboard_buttons.append([InlineKeyboardButton(admin_btn, callback_data="cmd_admin")])
    
    # Add back button
    keyboard_buttons.append([InlineKeyboardButton(back_btn, callback_data="help_help")])
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=translated_command,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

    await callback.answer()
    return

async def handle_command_callbacks(client, callback):
    user_id = callback.from_user.id
    callback_data = callback.data
    
    if callback_data == "cmd_ai":
        # Show AI commands
        translated_text = await async_translate_to_lang(ai_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands")]
        ])
        
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        
    elif callback_data == "cmd_img":
        # Show Image commands
        translated_text = await async_translate_to_lang(image_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands")]
        ])
        
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        
    elif callback_data == "cmd_main":
        # Show main commands
        translated_text = await async_translate_to_lang(main_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands")]
        ])
        
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    
    elif callback_data == "cmd_admin":
        # Show admin commands (only for admins)
        if user_id in ADMINS:
            back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(back_btn, callback_data="commands")]
            ])
            
            await client.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.id,
                text=admin_commands_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        else:
            # User is not an admin, show unauthorized message
            await callback.answer("You don't have permission to view admin commands", show_alert=True)
    
    await callback.answer()
    return

async def command_inline_start(client, callback):
    user_id = callback.from_user.id
    texts_to_translate = [command__text, "🧠 AI Response", "🖼️ Image Generation", "📋 Main Commands", "🔙 Back"]
    translated_texts = await batch_translate(texts_to_translate, user_id)
    translated_command = translated_texts[0]
    ai_btn = translated_texts[1]
    img_btn = translated_texts[2]
    main_btn = translated_texts[3]
    back_btn = translated_texts[4]
    keyboard_buttons = [
        [InlineKeyboardButton(ai_btn, callback_data="cmd_ai_start")],
        [InlineKeyboardButton(img_btn, callback_data="cmd_img_start")],
        [InlineKeyboardButton(main_btn, callback_data="cmd_main_start")],
    ]
    if user_id in ADMINS:
        admin_btn = "⚙️ Admin Commands"
        keyboard_buttons.append([InlineKeyboardButton(admin_btn, callback_data="cmd_admin_start")])
    keyboard_buttons.append([InlineKeyboardButton(back_btn, callback_data="back")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    await client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=translated_command,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    await callback.answer()
    return

async def command_inline_help(client, callback):
    user_id = callback.from_user.id
    texts_to_translate = [command__text, "🧠 AI Response", "🖼️ Image Generation", "📋 Main Commands", "🔙 Back"]
    translated_texts = await batch_translate(texts_to_translate, user_id)
    translated_command = translated_texts[0]
    ai_btn = translated_texts[1]
    img_btn = translated_texts[2]
    main_btn = translated_texts[3]
    back_btn = translated_texts[4]
    keyboard_buttons = [
        [InlineKeyboardButton(ai_btn, callback_data="cmd_ai_help")],
        [InlineKeyboardButton(img_btn, callback_data="cmd_img_help")],
        [InlineKeyboardButton(main_btn, callback_data="cmd_main_help")],
    ]
    if user_id in ADMINS:
        admin_btn = "⚙️ Admin Commands"
        keyboard_buttons.append([InlineKeyboardButton(admin_btn, callback_data="cmd_admin_help")])
    keyboard_buttons.append([InlineKeyboardButton(back_btn, callback_data="help_help")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    await client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=translated_command,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    await callback.answer()
    return

async def handle_command_callbacks_start(client, callback):
    user_id = callback.from_user.id
    callback_data = callback.data
    if callback_data == "cmd_ai_start":
        translated_text = await async_translate_to_lang(ai_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands_start")]
        ])
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    elif callback_data == "cmd_img_start":
        translated_text = await async_translate_to_lang(image_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands_start")]
        ])
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    elif callback_data == "cmd_main_start":
        translated_text = await async_translate_to_lang(main_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands_start")]
        ])
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    elif callback_data == "cmd_admin_start":
        if user_id in ADMINS:
            back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(back_btn, callback_data="commands_start")]
            ])
            await client.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.id,
                text=admin_commands_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        else:
            await callback.answer("You don't have permission to view admin commands", show_alert=True)
    await callback.answer()
    return

async def handle_command_callbacks_help(client, callback):
    user_id = callback.from_user.id
    callback_data = callback.data
    if callback_data == "cmd_ai_help":
        translated_text = await async_translate_to_lang(ai_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands_help")]
        ])
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    elif callback_data == "cmd_img_help":
        translated_text = await async_translate_to_lang(image_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands_help")]
        ])
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    elif callback_data == "cmd_main_help":
        translated_text = await async_translate_to_lang(main_commands_text, user_id)
        back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(back_btn, callback_data="commands_help")]
        ])
        await client.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=translated_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
    elif callback_data == "cmd_admin_help":
        if user_id in ADMINS:
            back_btn = await translate_ui_element("🔙 Back to Commands", user_id)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(back_btn, callback_data="commands_help")]
            ])
            await client.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.id,
                text=admin_commands_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        else:
            await callback.answer("You don't have permission to view admin commands", show_alert=True)
    await callback.answer()
    return


