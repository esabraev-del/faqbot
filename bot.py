#!/usr/bin/env python3
"""
Telegram FAQ Bot — КазНПУ Астана / КазНПУ Астана
Двуязычный бот (рус/каз) с FAQ из Google Sheets
"""

import os
import logging
import urllib.request
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8897221236:AAF33EvuJJdSyKmosn2XfC-206eEeDQ9KW8")

# ID вашей Google Таблицы
SPREADSHEET_ID = "1oS5ggbGTzoCDZbyGQpg04eVBnb4ZX6TSU0x5aoUc53g"
# Название листа
SHEET_NAME = "FAQ"

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Загрузка FAQ из Google Sheets ───────────────────────────────────────
def load_faq() -> dict:
    url = (
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
        f"/gviz/tq?tqx=out:json&sheet={SHEET_NAME}"
    )
    with urllib.request.urlopen(url) as resp:
        raw = resp.read().decode("utf-8")
    # Google возвращает не чистый JSON, убираем обёртку
    raw = raw[raw.index("{"):raw.rindex("}") + 1]
    data = json.loads(raw)

    rows = data["table"]["rows"]
    categories = {}
    cat_order = []

    for row in rows:
        cells = row.get("c", [])
        def val(i):
            if i < len(cells) and cells[i] and cells[i].get("v") is not None:
                return str(cells[i]["v"]).strip()
            return ""
        cat_ru, cat_kz, cat_id, q_ru, q_kz, a_ru, a_kz = (val(i) for i in range(7))
        if not cat_id or not q_ru:
            continue
        if cat_id not in categories:
            categories[cat_id] = {"id": cat_id, "ru": cat_ru, "kz": cat_kz, "questions": []}
            cat_order.append(cat_id)
        q_id = f"{cat_id}_{len(categories[cat_id]['questions'])}"
        categories[cat_id]["questions"].append({
            "id": q_id, "ru_q": q_ru, "kz_q": q_kz, "ru_a": a_ru, "kz_a": a_kz
        })

    return {"categories": [categories[k] for k in cat_order]}

# ─── Тексты интерфейса ────────────────────────────────────────────────────
UI = {
    "ru": {
        "welcome": "👋 Добро пожаловать в бот КазНПУ Астана!\n\nВыберите язык / Тілді таңдаңыз:",
        "choose_category": "📂 Выберите раздел:",
        "choose_question": "❓ Выберите вопрос:",
        "back_categories": "◀️ Назад к разделам",
        "back_questions": "◀️ Назад к вопросам",
        "back_main": "🏠 Главное меню",
        "lang_button": "🇰🇿 Қазақша",
        "help": "ℹ️ Бот отвечает на вопросы об университете.\n\nИспользуйте /start для возврата в меню.",
        "no_data": "⚠️ Данные ещё не добавлены. Заполните Google Таблицу.",
    },
    "kz": {
        "welcome": "👋 ҚазҰПУ Астана ботына қош келдіңіз!\n\nТілді таңдаңыз / Выберите язык:",
        "choose_category": "📂 Бөлімді таңдаңыз:",
        "choose_question": "❓ Сұрақты таңдаңыз:",
        "back_categories": "◀️ Бөлімдерге оралу",
        "back_questions": "◀️ Сұрақтарға оралу",
        "back_main": "🏠 Басты мәзір",
        "lang_button": "🇷🇺 Русский",
        "help": "ℹ️ Бот университет туралы сұрақтарға жауап береді.\n\n/start — басты мәзір.",
        "no_data": "⚠️ Деректер әлі қосылмаған. Google Кестені толтырыңыз.",
    },
}

def get_lang(context): return context.user_data.get("lang", "ru")

def keyboard_language():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang:kz"),
    ]])

def keyboard_categories(lang):
    faq = load_faq()
    if not faq["categories"]:
        return None
    buttons = [[InlineKeyboardButton(
        cat["ru"] if lang == "ru" else cat["kz"], callback_data=f"cat:{cat['id']}"
    )] for cat in faq["categories"]]
    buttons.append([InlineKeyboardButton(UI[lang]["lang_button"], callback_data="switch_lang")])
    return InlineKeyboardMarkup(buttons)

def keyboard_questions(cat_id, lang):
    faq = load_faq()
    cat = next((c for c in faq["categories"] if c["id"] == cat_id), None)
    if not cat:
        return None
    buttons = []
    for q in cat["questions"]:
        label = q["ru_q"] if lang == "ru" else q["kz_q"]
        if len(label) > 60: label = label[:57] + "..."
        buttons.append([InlineKeyboardButton(label, callback_data=f"q:{q['id']}")])
    buttons.append([InlineKeyboardButton(UI[lang]["back_categories"], callback_data="back_categories")])
    return InlineKeyboardMarkup(buttons)

def keyboard_answer(cat_id, lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(UI[lang]["back_questions"], callback_data=f"cat:{cat_id}")],
        [InlineKeyboardButton(UI[lang]["back_main"], callback_data="back_main")],
    ])

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("lang", None)
    await update.message.reply_text(UI["ru"]["welcome"], reply_markup=keyboard_language())

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(UI[get_lang(context)]["help"])

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)

    if data.startswith("lang:"):
        lang = data.split(":")[1]
        context.user_data["lang"] = lang
        kb = keyboard_categories(lang)
        if kb:
            await query.edit_message_text(UI[lang]["choose_category"], reply_markup=kb)
        else:
            await query.edit_message_text(UI[lang]["no_data"])

    elif data == "switch_lang":
        lang = "kz" if lang == "ru" else "ru"
        context.user_data["lang"] = lang
        kb = keyboard_categories(lang)
        if kb:
            await query.edit_message_text(UI[lang]["choose_category"], reply_markup=kb)
        else:
            await query.edit_message_text(UI[lang]["no_data"])

    elif data.startswith("cat:"):
        cat_id = data.split(":", 1)[1]
        context.user_data["current_cat"] = cat_id
        kb = keyboard_questions(cat_id, lang)
        if kb:
            await query.edit_message_text(UI[lang]["choose_question"], reply_markup=kb)

    elif data.startswith("q:"):
        q_id = data.split(":", 1)[1]
        faq = load_faq()
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
        await query.edit_message_text(
            f"❓ *{q_text}*\n\n{a_text}",
            parse_mode="Markdown",
            reply_markup=keyboard_answer(cat_id, lang),
        )

    elif data == "back_categories":
        kb = keyboard_categories(lang)
        if kb:
            await query.edit_message_text(UI[lang]["choose_category"], reply_markup=kb)

    elif data == "back_main":
        context.user_data.pop("lang", None)
        await query.edit_message_text(UI["ru"]["welcome"], reply_markup=keyboard_language())

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(callback_handler))
    logger.info("Бот запущен...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
