import pyrogram
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaAnimation
from pyrogram.types import InlineQuery
from typing import Union
from modules.lang import async_translate_to_lang, batch_translate, format_with_mention
from modules.chatlogs import channel_log
import database.user_db as user_db
from pyrogram.enums import ParseMode
from config import ADMIN_CONTACT_MENTION, OWNER_ID
from modules.user.premium_management import get_premium_benefits_message, get_premium_status_message
from modules.user.ai_model import TEXT_MODELS, IMAGE_MODELS

# Import for benefits display
# Define button texts with emojis - NO premium button here
button_list = [
    "➕ Добавить в группу",
    "🛠️ Команды",
    "❓ Помощь",
    "⚙️ Настройки",
    "📞 Поддержка",
    "💎 Получить премиум"
]

welcome_text = """
✨ **Добро пожаловать, {user_mention}!** ✨

🤖 **ChatAll**

Я могу помочь вам с:

🧠 **Умный чат** — интеллектуальные беседы с мультимодельным ИИ
🗣️ **Голос и текст** — преобразование голоса в текст и обратно
🖼️ **Создание изображений** — генерация потрясающих картинок из текста
📝 **Извлечение текста** — анализ текста на изображениях
🌐 **Мультиязычность** — общение на вашем языке

━━━━━━━━━━━━━━━━━━━━━

<b>🧠 Поддерживаемые текстовые модели ИИ:</b>
""" + ", ".join(TEXT_MODELS.values()) + """

<b>🖼️ Поддерживаемые модели генерации изображений:</b>
""" + ", ".join(IMAGE_MODELS.values()) + """

<b>✨ Поддержка нескольких моделей:</b> Вы можете выбрать предпочитаемые текстовые и графические модели в Настройках → Панель моделей ИИ.

**Выберите кнопку ниже, чтобы начать!**
"""

tip_text = "💡 **Совет:** Напишите любое сообщение, чтобы начать общение со мной, **или**\nиспользуйте `/img` с вашим запросом для генерации изображений!\n**Больше команд: /help.**"

LOGO = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnp4MnR0YXk3ZGNjenR6NGRoaDNkc2h2NDgxa285NnExaGM1MTZmYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/S60CrN9iMxFlyp7uM8/giphy.gif"

async def start(client, message: Message):
    await user_db.check_and_add_user(message.from_user.id)
    if message.from_user.username:
        await user_db.check_and_add_username(message.from_user.id, message.from_user.username)

    user_id = message.from_user.id
    mention = message.from_user.mention
    user_lang = user_db.get_user_language(user_id)
    translated_welcome = await format_with_mention(welcome_text.replace("{user_mention}", "{mention}"), mention, user_id, user_lang)
    translated_texts = await batch_translate([tip_text] + button_list, user_id)
    translated_tip = translated_texts[0]
    translated_buttons = translated_texts[1:]

    keyboard_layout = [
        [InlineKeyboardButton(translated_buttons[0], url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton(translated_buttons[1], callback_data="commands_start"),
         InlineKeyboardButton(translated_buttons[2], callback_data="help_start")],
        [InlineKeyboardButton(translated_buttons[3], callback_data="settings"),
         InlineKeyboardButton(translated_buttons[4], callback_data="support")],
        [InlineKeyboardButton(translated_buttons[5], callback_data="premium_info")]
    ]
    keyboard = InlineKeyboardMarkup(keyboard_layout)

    await client.send_animation(chat_id=message.chat.id, animation=LOGO, caption=translated_welcome, reply_markup=keyboard)
    #if user is premium, skip the tip

    premium_message = await get_premium_status_message(user_id)
    if not premium_message:
        await message.reply_text(translated_tip)

async def start_inline(bot, callback: CallbackQuery):
    user_id = callback.from_user.id
    mention = callback.from_user.mention
    user_lang = user_db.get_user_language(user_id)
    translated_welcome = await format_with_mention(welcome_text.replace("{user_mention}", "{mention}"), mention, user_id, user_lang)
    translated_buttons = await batch_translate(button_list, user_id)

    keyboard_layout = [
        [InlineKeyboardButton(translated_buttons[0], url=f"https://t.me/{bot.me.username}?startgroup=true")],
        [InlineKeyboardButton(translated_buttons[1], callback_data="commands_start"),
         InlineKeyboardButton(translated_buttons[2], callback_data="help_start")],
        [InlineKeyboardButton(translated_buttons[3], callback_data="settings"),
         InlineKeyboardButton(translated_buttons[4], callback_data="support")],
        [InlineKeyboardButton(translated_buttons[5], callback_data="premium_info")]
    ]
    keyboard = InlineKeyboardMarkup(keyboard_layout)

    await bot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.id, caption=translated_welcome, reply_markup=keyboard)

async def premium_info_page(client_or_bot, update_obj: Union[Message, CallbackQuery], is_callback: bool = False):
    """Sends or edits message to show premium benefits. Can be called by command or callback."""
    user_id = update_obj.from_user.id
    benefits_text = await get_premium_benefits_message(user_id)
    btn_get_sub_text = await async_translate_to_lang("💳 Получить подписку", user_id)
    btn_back_text = await async_translate_to_lang("🔙 Назад", user_id)

    keyboard_buttons = [
        [InlineKeyboardButton(btn_get_sub_text, callback_data="premium_plans")],
        # This button takes user back to the main start panel from the benefits page
        [InlineKeyboardButton(btn_back_text, callback_data="back")] 
    ]
    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    if is_callback:
        callback_query = update_obj
        # If current message has a photo (e.g. QR code), change it to LOGO animation
        if callback_query.message.photo:
            try:
                await client_or_bot.edit_message_media(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.id,
                    media=InputMediaAnimation(LOGO),
                )
                # Edit caption separately after media is changed
                await client_or_bot.edit_message_caption(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.id,
                    caption=benefits_text,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                print(f"Error editing media/caption for premium_info_page (photo to animation): {e}")
                # Fallback to sending a new message if edit fails catastrophically
                await client_or_bot.send_animation(
                    chat_id=callback_query.message.chat.id,
                    animation=LOGO,
                    caption=benefits_text,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
                await callback_query.message.delete() # Delete old message if we sent a new one
        else: # If current message is text or animation (already LOGO), just edit caption/text
            try:
                if callback_query.message.animation or callback_query.message.caption: # If it has caption (animation or text with media)
                    await client_or_bot.edit_message_caption(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.id,
                        caption=benefits_text,
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML
                    )
                else: # Plain text message
                    await client_or_bot.edit_message_text(
                        chat_id=callback_query.message.chat.id,
                        message_id=callback_query.message.id,
                        text=benefits_text,
                        reply_markup=keyboard,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
            except Exception as e:
                print(f"Error editing message for premium_info_page (text/animation): {e}")
                # Fallback: send new message if edit fails
                await client_or_bot.send_animation(
                    chat_id=callback_query.message.chat.id, animation=LOGO, caption=benefits_text, 
                    reply_markup=keyboard, parse_mode=ParseMode.HTML
                )
                # Try to delete the old message if sending new one
                try: await callback_query.message.delete() 
                except: pass
        await callback_query.answer()
    else: # Called from /premiumsubscribe command (Message object)
        message = update_obj
        # Send a new message with the LOGO animation and benefits text
        await client_or_bot.send_animation(
            chat_id=message.chat.id,
            animation=LOGO,
            caption=benefits_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

async def premium_plans_callback(client: pyrogram.Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    plans_title = await async_translate_to_lang("💎 **Премиум тарифы** 💎", user_id)
    plan1_text = await async_translate_to_lang("249₽ — доступ на неделю", user_id)
    plan2_text = await async_translate_to_lang("899₽ — доступ на месяц (выгодно)", user_id)
    plan3_text = await async_translate_to_lang("9499₽ — доступ на год (максимальная выгода)", user_id)
    paid_button_text = await async_translate_to_lang("✅ Я оплатил", user_id)
    back_button_text = await async_translate_to_lang("🔙 Назад к преимуществам", user_id)

    text = f"{plans_title}\n\n"
    text += f"🔹 {plan1_text}\n"
    text += f"🔹 {plan2_text}\n"
    text += f"🔹 {plan3_text}\n\n"
    text += await async_translate_to_lang(
        "После оплаты нажмите кнопку ниже, чтобы уведомить администратора и **отправьте скриншот платежа {admin_contact}** для быстрой проверки.\n\n".replace(
            "{admin_contact}",
            ADMIN_CONTACT_MENTION if ADMIN_CONTACT_MENTION else f"владельцу бота (ID: {OWNER_ID})",
        ),
        user_id,
    )
    
    pay_249 = InlineKeyboardButton("💳 249 ₽", callback_data="yookassa_pay_249")
    pay_899 = InlineKeyboardButton("💳 899 ₽", callback_data="yookassa_pay_899")
    pay_9499 = InlineKeyboardButton("💳 9499 ₽", callback_data="yookassa_pay_9499")
    keyboard = InlineKeyboardMarkup([
        [pay_249, pay_899],
        [pay_9499],
        [InlineKeyboardButton(paid_button_text, callback_data="premium_paid_notify")],
        [InlineKeyboardButton(back_button_text, callback_data="premium_info")]
    ])

    try:
        if callback_query.message.animation or callback_query.message.photo:
            await client.edit_message_caption(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.id,
                caption=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await client.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.id,
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )
    except Exception as e:
        print(f"Error editing message for premium_plans_callback: {e}. Fallback: sending new message.")
        try:
            await callback_query.message.delete()
        except Exception:
            pass
        await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN,
        )
    await callback_query.answer()

async def premium_paid_notify_callback(client: pyrogram.Client, callback_query: CallbackQuery):
    user = callback_query.from_user
    
    user_mention = user.mention if hasattr(user, 'mention') else f"<a href='tg://user?id={user.id}'>User {user.id}</a>"
    username_str = f"@{user.username}" if user.username else "N/A"

    admin_notification_text = (
        f"🔔 **Уведомление об оплате премиум** 🔔\n\n"
        f"👤 **Данные пользователя:**\n"
        f"    Упоминание: {user_mention}\n"
        f"    Username: {username_str}\n"
        f"    ID: `{user.id}`\n\n"
        f"💰 Пользователь сообщил об оплате премиума.\n\n"
        f"👉 **Необходимо проверить платеж**\n"
        f"    После подтверждения выдать премиум командой:\n"
        f"    `/premium {user.id} <дней>`\n\n"
        f"Спасибо! ✨"
    )
    
    admin_to_notify = OWNER_ID 
    try:
        # Ensure Markdown is parsed for the admin notification
        await client.send_message(admin_to_notify, admin_notification_text)
    except Exception as e:
        print(f"Error sending premium paid notification to admin {admin_to_notify}: {e}")

    user_reply_base = "✅ Уведомление об оплате отправлено администратору. **Пожалуйста, отправьте скриншот платежа {admin_contact} для быстрой проверки.** Администратор свяжется с вами при возникновении вопросов или после активации премиума."
    admin_contact_text = ADMIN_CONTACT_MENTION if ADMIN_CONTACT_MENTION else f"владельцу бота (ID: {OWNER_ID})"
    user_reply_text_formatted = user_reply_base.replace("{admin_contact}", admin_contact_text)
    user_reply_text_translated = await async_translate_to_lang(user_reply_text_formatted, user.id)
    
    btn_back_to_plans_text = await async_translate_to_lang("💳 Вернуться к тарифам", user.id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_back_to_plans_text, callback_data="premium_plans")]
    ])

    try:
        await client.edit_message_caption(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.id, 
            caption=user_reply_text_translated, 
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error editing message caption for paid notify: {e}. Trying to send new message.")
        await client.send_message(
             chat_id=callback_query.message.chat.id,
             text=user_reply_text_translated,
             reply_markup=keyboard
        )
        try: await callback_query.message.delete() 
        except: pass
    await callback_query.answer("Уведомление отправлено администратору! Не забудьте прислать ему скриншот.", show_alert=True)


PAYMENT_PLANS = {
    '249': {'amount': 249, 'days': 7},
    '899': {'amount': 899, 'days': 30},
    '9499': {'amount': 9499, 'days': 365}
}

async def yookassa_pay_callback(client: pyrogram.Client, callback_query: CallbackQuery):
    key = callback_query.data.split('_')[-1]
    plan = PAYMENT_PLANS.get(key)
    if not plan:
        await callback_query.answer("Неизвестный тариф", show_alert=True)
        return
    from modules.payment.yookassa_service import create_payment
    url, payment_id = await create_payment(callback_query.from_user.id, plan['amount'], plan['days'])
    pay_text = await async_translate_to_lang("Нажмите кнопку ниже для оплаты через YooKassa", callback_query.from_user.id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Оплатить", url=url)],
        [InlineKeyboardButton("✅ Оплатил", callback_data=f'check_payment_{payment_id}')]
    ])
    await client.send_message(callback_query.message.chat.id, pay_text, reply_markup=keyboard)
    await callback_query.answer()

async def check_payment_status_callback(client: pyrogram.Client, callback_query: CallbackQuery):
    payment_id = callback_query.data.split('_', 2)[2]
    from modules.payment.yookassa_service import verify_payment
    success = await verify_payment(payment_id)
    if success:
        msg = await async_translate_to_lang("Оплата прошла успешно! Премиум активирован.", callback_query.from_user.id)
        await callback_query.answer(msg, show_alert=True)
    else:
        msg = await async_translate_to_lang("Оплата еще не завершена.", callback_query.from_user.id)
        await callback_query.answer(msg, show_alert=True)

