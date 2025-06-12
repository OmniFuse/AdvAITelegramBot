import pyrogram
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import Message
from pyrogram.types import InlineQuery
from pyrogram.types import CallbackQuery
from modules.lang import async_translate_to_lang, batch_translate, translate_ui_element
from modules.chatlogs import channel_log


help_text = """
✨ **ЦЕНТР ПОМОЩИ ChatAll** ✨

━━━━━━━━━━━━━━━━━━━

**ВЫБЕРИТЕ КАТЕГОРИЮ НИЖЕ:**
"""

ai_chat_help = """
🧠 **ПОМОЩНИК AI-ЧАТА** 🧠

━━━━━━━━━━━━━━━━━━━

Бот использует **GPT-4o** для умных ответов на любые вопросы.

**ОСНОВНЫЕ ВОЗМОЖНОСТИ:**
• 💬 **Учитывает контекст** — помнит историю беседы
• 🧩 **Сложные вопросы** — развёрнутые ответы
• 💻 **Генерация кода** — с подсветкой синтаксиса
• 🔢 **Решение задач** — помогает с уравнениями
• 🌎 **Перевод** — работает на разных языках

**КОМАНДЫ:**
• 💬 В личных чатах: просто напишите сообщение
• 🔄 В группах: используйте `/ai`, `/ask` или `/say` + вопрос
• 🆕 Сбросить чат: `/new` или `/newchat`

**ПРИМЕР:**
`/ai чем квантовые вычисления отличаются от классических?`

**💡 СОВЕТ:** для вопросов по коду указывайте язык программирования.
"""

image_gen_help = """
🖼️ **ГЕНЕРАЦИЯ ИЗОБРАЖЕНИЙ** 🖼️

━━━━━━━━━━━━━━━━━━━

Создавайте впечатляющие изображения по текстовому описанию.

**ОСНОВНЫЕ ВОЗМОЖНОСТИ:**
• 🎨 **Высокое качество** — детализированные и реалистичные картинки
• 🏞️ **Разные стили** — реализм, арт, скетч, 3D
• 🔄 **Перегенерация** — повтор с тем же запросом одной кнопкой
• 👥 **Работает везде** — в личных чатах и группах

**КОМАНДЫ:**
• 📝 `/generate [запрос]` — полная команда
• 📸 `/img [запрос]` — короткая версия
• 🖌️ `/gen [запрос]` — самая короткая

**ПРИМЕР:**
`/img киберпанк-город ночью с неоном и летающими машинами`

**💡 СОВЕТЫ:**
• Указывайте детали, освещение и перспективу
• Добавляйте художественные ссылки для лучшего результата
• Пробуйте разные стили для разнообразия
"""

voice_features_help = """
🎙️ **ГОЛОСОВЫЕ ФУНКЦИИ** 🎙️

━━━━━━━━━━━━━━━━━━━

Преобразование речи и текста с помощью продвинутых технологий.

**ОСНОВНЫЕ ВОЗМОЖНОСТИ:**
• 🗣️ **Речь в текст** — расшифровка голосовых сообщений
• 🔊 **Текст в речь** — озвучивание ответов
• 🌐 **Мультиязычность** — поддержка разных языков
• 💬 **Диалог** — задавайте вопросы голосом

**КАК ИСПОЛЬЗОВАТЬ:**
1. 🎤 Отправьте голосовое сообщение
2. 📝 Бот превратит его в текст
3. 💬 Получите ответ на вопрос
4. ⚙️ Настройте параметры голоса в меню настроек

**💡 СОВЕТЫ:**
• Говорите чётко и без посторонних шумов
• Держите сообщения короче 1 минуты
• Выберите предпочтительный язык голоса в настройках
"""

image_analysis_help = """
🔍 **АНАЛИЗ ИЗОБРАЖЕНИЙ** 🔍

━━━━━━━━━━━━━━━━━━━

Извлекайте и анализируйте текст с любых изображений с помощью OCR.

**ОСНОВНЫЕ ВОЗМОЖНОСТИ:**
• 📱 **Распознавание текста** — фото и скриншоты
• 📄 **Сканирование документов** — печатные материалы
• ❓ **Дополнительные вопросы** — спрашивайте о найденном тексте
• 📊 **Распознавание данных** — таблицы, чеки и другое

**КАК ИСПОЛЬЗОВАТЬ:**
1. 📷 Отправьте изображение с текстом
2. 🔍 Бот извлечёт весь читаемый текст
3. 💬 Задайте вопросы по содержимому
4. 📱 В группах добавьте "ai" в подпись к изображению

**💡 СОВЕТЫ:**
• Используйте хорошее освещение для лучшего распознавания
• Фотографируйте текст прямо, без наклонов
• Обрезайте фото, оставляя важную область
"""

quick_start_help = """
🚀 **КРАТКОЕ РУКОВОДСТВО** 🚀

━━━━━━━━━━━━━━━━━━━

**ВСЕГО 3 ШАГА:**

1️⃣ **Общение с ИИ**
   • В личке: просто отправьте сообщение
   • В группах: используйте команду `/ai`

2️⃣ **Создание изображений**
   • Введите `/img` и описание
   • Пример: `/img закат над горами`

3️⃣ **Анализ изображений**
   • Отправьте любое изображение с текстом
   • Бот извлечёт текст и проанализирует его

**ПОЛЕЗНЫЕ КОМАНДЫ:**
• `/start` — главное меню
• `/help` — этот справочник
• `/settings` — настройки бота
• `/new` — очистить историю диалога

**ПРОБЛЕМЫ?**
• Нажмите «Поддержка» в главном меню
• Сформулируйте запрос точнее для лучшего результата
"""


async def help(client, message):
    user_id = message.from_user.id
    
    # Translate help text and button labels
    texts_to_translate = [
        help_text, 
        "🧠 ИИ Чат", 
        "🖼️ Генерации", 
        "🎙️ Голосовые функции",
        "🔍 Анализ изображений",
        "🚀 Быстрый старт",
        "📋 Команды"
    ]
    
    translated_texts = await batch_translate(texts_to_translate, user_id)
    
    translated_help = translated_texts[0]
    ai_btn = translated_texts[1]
    img_btn = translated_texts[2]
    voice_btn = translated_texts[3]
    analysis_btn = translated_texts[4]
    quickstart_btn = translated_texts[5]
    cmd_btn = translated_texts[6]
    
    # Create interactive keyboard with feature categories
    # No back button when accessed directly through /help command
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(ai_btn, callback_data="help_ai")],
        [InlineKeyboardButton(img_btn, callback_data="help_img")],
        [InlineKeyboardButton(voice_btn, callback_data="help_voice")],
        [InlineKeyboardButton(analysis_btn, callback_data="help_analysis")],
        [InlineKeyboardButton(quickstart_btn, callback_data="help_quickstart")],
        [InlineKeyboardButton(cmd_btn, callback_data="commands")]
    ])
    
    await client.send_message(
        chat_id=message.chat.id,
        text=translated_help,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

async def help_inline_start(bot, callback):
    user_id = callback.from_user.id
    texts_to_translate = [
        help_text,"🧠 ИИ Чат", 
        "🖼️ Генерации", 
        "🎙️ Голосовые функции",
        "🔍 Анализ изображений",
        "🚀 Быстрый старт","🔙 Назад"
    ]
    translated_texts = await batch_translate(texts_to_translate, user_id)
    translated_help = translated_texts[0]
    ai_btn = translated_texts[1]
    img_btn = translated_texts[2]
    voice_btn = translated_texts[3]
    analysis_btn = translated_texts[4]
    quickstart_btn = translated_texts[5]
    cmd_btn = translated_texts[6]
    back_btn = translated_texts[7]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(ai_btn, callback_data="help_ai_start")],
        [InlineKeyboardButton(img_btn, callback_data="help_img_start")],
        [InlineKeyboardButton(voice_btn, callback_data="help_voice_start")],
        [InlineKeyboardButton(analysis_btn, callback_data="help_analysis_start")],
        [InlineKeyboardButton(quickstart_btn, callback_data="help_quickstart_start")],
        [InlineKeyboardButton(cmd_btn, callback_data="commands_start")],
        [InlineKeyboardButton(back_btn, callback_data="back")]
    ])
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=translated_help,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    await callback.answer()
    return

async def help_inline_help(bot, callback):
    user_id = callback.from_user.id
    texts_to_translate = [
        help_text,"🧠 ИИ Чат", 
        "🖼️ Генерации", 
        "🎙️ Голосовые функции",
        "🔍 Анализ изображений",
        "🚀 Быстрый старт","🔙 Назад"
    ]
    translated_texts = await batch_translate(texts_to_translate, user_id)
    translated_help = translated_texts[0]
    ai_btn = translated_texts[1]
    img_btn = translated_texts[2]
    voice_btn = translated_texts[3]
    analysis_btn = translated_texts[4]
    quickstart_btn = translated_texts[5]
    cmd_btn = translated_texts[6]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(ai_btn, callback_data="help_ai_help")],
        [InlineKeyboardButton(img_btn, callback_data="help_img_help")],
        [InlineKeyboardButton(voice_btn, callback_data="help_voice_help")],
        [InlineKeyboardButton(analysis_btn, callback_data="help_analysis_help")],
        [InlineKeyboardButton(quickstart_btn, callback_data="help_quickstart_help")],
        [InlineKeyboardButton(cmd_btn, callback_data="commands_help")]
    ])
    await bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=translated_help,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    await callback.answer()
    return
    
async def handle_help_category(client, callback):
    user_id = callback.from_user.id
    callback_data = callback.data
    # Determine entry point
    is_start = callback_data.endswith('_start')
    help_content = help_text  # Default
    if 'ai' in callback_data:
        help_content = ai_chat_help
    elif 'img' in callback_data:
        help_content = image_gen_help
    elif 'voice' in callback_data:
        help_content = voice_features_help
    elif 'analysis' in callback_data:
        help_content = image_analysis_help
    elif 'quickstart' in callback_data:
        help_content = quick_start_help
    translated_text = await async_translate_to_lang(help_content, user_id)
    back_btn = await translate_ui_element("🔙 Назад в меню помощи", user_id)
    # Use correct callback_data for back button
    back_callback = "help_start" if is_start else "help_help"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(back_btn, callback_data=back_callback)]
    ])
    await client.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=translated_text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
    await callback.answer()
    return
    
