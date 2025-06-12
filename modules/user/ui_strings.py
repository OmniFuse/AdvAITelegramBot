"""
Module containing all UI strings used in the bot for easy translation.
"""

# Start and Help commands
START_MESSAGE = """
👋 Добро пожаловать в ChatAll!

Я ваш продвинутый AI‑ассистент на базе современных технологий.

🔸 Общайтесь со мной напрямую
🔸 Отправляйте голосовые сообщения
🔸 Генерируйте изображения командой /img
🔸 Изменяйте настройки через /settings
🔸 Очищайте историю чата командой /new

💡 Для дополнительной информации используйте /help
"""

HELP_MESSAGE = """
**Справка ChatAll**

**Команды:**
• /start — запустить бота
• /help — показать это меню
• /settings — настройки бота
• /new или /newchat — начать новый диалог
• /img [prompt] — создать изображение
• /rate — оценить бота

**Возможности:**
• Отправляйте текстовые сообщения для ответа ИИ
• Записывайте голосовые сообщения
• Отправляйте изображения для распознавания текста
• В группах используйте /ai для общения с ботом

Нужна дополнительная помощь? Откройте меню настроек и выберите язык, голос и другие параметры.
"""

# Settings UI
SETTINGS_MAIN = "⚙️ **Настройки бота**\n\nНастройте работу ChatAll под себя"
SETTINGS_VOICE = "🎙️ **Настройки голоса**\n\nТекущий режим: {}\n\nВыберите, как получать ответы на голосовые сообщения"
SETTINGS_LANGUAGE = "🌐 **Настройки языка**\n\nТекущий язык: {}\n\nВыберите предпочитаемый язык интерфейса"
SETTINGS_ASSISTANT = "🤖 **Режим ассистента**\n\nТекущий режим: {}\n\nВыберите стиль работы AI‑ассистента"
SETTINGS_SUPPORT = "📞 **Поддержка**\n\nПолучите помощь по использованию бота"

# Buttons
BTN_BACK = "🔙 Назад"
BTN_SETTINGS = "⚙️ Настройки"
BTN_HELP = "❓ Помощь"
BTN_COMMANDS = "📋 Команды"

# Voice settings
VOICE_SETTING_UPDATED = "Режим голосовых сообщений изменён на: {}"
TEXT_MODE = "Текстовый режим"
VOICE_MODE = "Голосовой режим"

# Language settings
LANGUAGE_UPDATED = "Язык изменён на: {}"

# Assistant modes
MODE_UPDATED = "Режим ассистента изменён на: {}"
MODE_CHATBOT = "Чат-бот"
MODE_CODER = "Программист"
MODE_PROFESSIONAL = "Профессионал"
MODE_TEACHER = "Учитель"
MODE_THERAPIST = "Терапевт"
MODE_ASSISTANT = "Ассистент"
MODE_GAMER = "Геймер"
MODE_TRANSLATOR = "Переводчик"

# Image generation
GENERATING_IMAGES = "🖼️ Генерирую изображения. Пожалуйста, подождите..."
IMAGES_GENERATED = "Сгенерированные изображения по запросу: {}"

# Voice messages
PROCESSING_VOICE = "🎙️ Обрабатываю ваше голосовое сообщение..."
VOICE_NOT_UNDERSTOOD = "Извините, не удалось распознать аудио."
VOICE_SERVICE_ERROR = "Возникла проблема с сервисом распознавания речи. Попробуйте позже."

# OCR
EXTRACTING_TEXT = "🔍 Извлекаю текст с изображения..."
OCR_ERROR = "Ошибка: не удалось извлечь текст из изображения. {}"

# New chat
CHAT_CLEARED = "История чата очищена. Можете начать новый диалог."

# Rate bot
RATE_MESSAGE = "⭐ Оцените работу ChatAll"
RATE_THANK_YOU = "Спасибо за отзыв! Ваша оценка: {}/5"

# Error messages
ERROR_OCCURRED = "Произошла ошибка: {}"
COMMAND_NOT_ALLOWED = "Вам нельзя использовать эту команду."
