#!/usr/bin/env python3
"""
Telegram FAQ Bot — ФКиНВП / ФКжНВП факультеті
Двуязычный бот (рус/каз) с inline-кнопками и FAQ из JSON
"""

import json
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ─── Настройки ─────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8897221236:AAF33EvuJJdSyKmosn2XfC-206eEeDQ9KW8")
FAQ_FILE = os.path.join(os.path.dirname(__file__), "faq.json")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Загрузка FAQ ──────────────────────────────────────────────────────────
def load_faq() -> dict:
    with open(FAQ_FILE, encoding="utf-8") as f:
        return json.load(f)

# ─── Тексты интерфейса ────────────────────────────────────────────────────
UI = {
    "ru": {
        "welcome": (
            "👋 Добро пожаловать в бот факультета ФКиНВП!\n\n"
            "Выберите язык / Тілді таңдаңыз:"
        ),
        "choose_category": "📂 Выберите раздел:",
        "choose_question": "❓ Выберите вопрос:",
        "back_categories": "◀️ Назад к разделам",
        "back_questions": "◀️ Назад к вопросам",
        "back_main": "🏠 Главное меню",
        "lang_button": "🇰🇿 Қазақша",
        "help": (
            "ℹ️ Этот бот отвечает на часто задаваемые вопросы о факультете.\n\n"
            "Используйте /start для возврата в главное меню."
        ),
    },
    "kz": {
        "welcome": (
            "👋 ФКжНВП факультетінің ботына қош келдіңіз!\n\n"
            "Тілді таңдаңыз / Выберите язык:"
        ),
        "choose_category": "📂 Бөлімді таңдаңыз:",
        "choose_question": "❓ Сұрақты таңдаңыз:",
        "back_categories": "◀️ Бөлімдерге оралу",
        "back_questions": "◀️ Сұрақтарға оралу",
        "back_main": "🏠 Басты мәзір",
        "lang_button": "🇷🇺 Русский",
        "help": (
            "ℹ️ Бұл бот факультет туралы жиі қойылатын сұрақтарға жауап береді.\n\n"
            "Басты мәзірге оралу үшін /start пайдаланыңыз."
        ),
    },
}

# ─── Утилиты ──────────────────────────────────────────────────────────────
def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "ru")

def lang_key(lang: str, key_ru: str, key_kz: str) -> str:
    return key_kz if lang == "kz" else key_ru

# ─── Клавиатуры ───────────────────────────────────────────────────────────
def keyboard_language() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang:kz"),
        ]
    ])

def keyboard_categories(lang: str) -> InlineKeyboardMarkup:
    faq = load_faq()
    buttons = []
    for cat in faq["categories"]:
        label = cat["ru"] if lang == "ru" else cat["kz"]
        buttons.append([InlineKeyboardButton(label, callback_data=f"cat:{cat['id']}")])
    # Кнопка смены языка
    buttons.append([InlineKeyboardButton(UI[lang]["lang_button"], callback_data="switch_lang")])
    return InlineKeyboardMarkup(buttons)

def keyboard_questions(cat_id: str, lang: str) -> InlineKeyboardMarkup:
    faq = load_faq()
    cat = next(c for c in faq["categories"] if c["id"] == cat_id)
    buttons = []
    for q in cat["questions"]:
        label = q["ru_q"] if lang == "ru" else q["kz_q"]
        # Обрезаем длинные вопросы для кнопки
        if len(label) > 60:
            label = label[:57] + "..."
        buttons.append([InlineKeyboardButton(label, callback_data=f"q:{q['id']}")])
    buttons.append([InlineKeyboardButton(UI[lang]["back_categories"], callback_data="back_categories")])
    return InlineKeyboardMarkup(buttons)

def keyboard_answer(cat_id: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(UI[lang]["back_questions"], callback_data=f"cat:{cat_id}")],
        [InlineKeyboardButton(UI[lang]["back_main"], callback_data="back_main")],
    ])

# ─── Хэндлеры ─────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start — показывает выбор языка"""
    context.user_data.pop("lang", None)
    await update.message.reply_text(
        UI["ru"]["welcome"],
        reply_markup=keyboard_language(),
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    await update.message.reply_text(UI[lang]["help"])

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)

    # Выбор языка
    if data.startswith("lang:"):
        lang = data.split(":")[1]
        context.user_data["lang"] = lang
        await query.edit_message_text(
            UI[lang]["choose_category"],
            reply_markup=keyboard_categories(lang),
        )

    # Смена языка
    elif data == "switch_lang":
        lang = "kz" if lang == "ru" else "ru"
        context.user_data["lang"] = lang
        await query.edit_message_text(
            UI[lang]["choose_category"],
            reply_markup=keyboard_categories(lang),
        )

    # Выбор категории
    elif data.startswith("cat:"):
        cat_id = data.split(":", 1)[1]
        context.user_data["current_cat"] = cat_id
        await query.edit_message_text(
            UI[lang]["choose_question"],
            reply_markup=keyboard_questions(cat_id, lang),
        )

    # Выбор вопроса
    elif data.startswith("q:"):
        q_id = data.split(":", 1)[1]
        faq = load_faq()
        # Найти вопрос и его категорию
        cat_id = context.user_data.get("current_cat", "")
        question = None
        for cat in faq["categories"]:
            for q in cat["questions"]:
                if q["id"] == q_id:
                    question = q
                    cat_id = cat["id"]
                    break
        if not question:
            await query.edit_message_text("Вопрос не найден.")
            return
        q_text = question["ru_q"] if lang == "ru" else question["kz_q"]
        a_text = question["ru_a"] if lang == "ru" else question["kz_a"]
        text = f"❓ *{q_text}*\n\n{a_text}"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard_answer(cat_id, lang),
        )

    # Назад к категориям
    elif data == "back_categories":
        await query.edit_message_text(
            UI[lang]["choose_category"],
            reply_markup=keyboard_categories(lang),
        )

    # Главное меню
    elif data == "back_main":
        context.user_data.pop("lang", None)
        await query.edit_message_text(
            UI["ru"]["welcome"],
            reply_markup=keyboard_language(),
        )

# ─── Запуск ───────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(callback_handler))
    logger.info("Бот запущен...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
