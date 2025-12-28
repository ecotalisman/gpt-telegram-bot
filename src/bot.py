from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

import html

from config import TG_BOT_API_KEY
from utils import load_messages


MODE_GPT = "gpt"
MODE_RANDOM = "random"
MODE_QUIZ = "quiz"
MODE_TALK = "talk"


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["/gpt", "/random", "/quiz", "/talk"],
            ["/start", "/reset"],
        ],
        resize_keyboard=True,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_messages("main")
    context.user_data["mode"] = MODE_GPT
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
    )


async def set_gpt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = MODE_GPT
    await update.message.reply_text(
        "✅ <b>GPT mode</b> enabled.\nWrite your question:",
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
    )


async def set_random_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = MODE_RANDOM
    await update.message.reply_text(
        "✅ <b>Random facts mode</b> enabled.\nSend any message and I’ll reply with a fact (stub for now).",
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
    )


async def set_quiz_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = MODE_QUIZ
    await update.message.reply_text(
        "✅ <b>Quiz mode</b> enabled.\nSend 'start' to begin (stub for now).",
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
    )


async def set_talk_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = MODE_TALK
    context.user_data["persona"] = "friendly_mentor"
    await update.message.reply_text(
        "🎭 <b>Talk mode</b> enabled.\nNow I’ll reply as your persona (stub).\nWrite something:",
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["mode"] = MODE_GPT
    await update.message.reply_text(
        "♻️ Reset done. Back to <b>GPT mode</b>.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    mode = context.user_data.get("mode", MODE_GPT)
    safe_text = html.escape(user_text)

    if mode == MODE_GPT:
        await update.message.reply_text(
            f"🤖 <b>GPT stub</b>\nYou wrote: <code>{safe_text}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    if mode == MODE_RANDOM:
        await update.message.reply_text(
            "🎲 <b>Random fact stub</b>\nDid you know? The first computer bug was an actual moth 🦋",
            parse_mode=ParseMode.HTML,
        )
        return

    if mode == MODE_QUIZ:
        if user_text.lower() == "start":
            await update.message.reply_text(
                "🧠 <b>Quiz stub</b>\nQ1: What is Python?\nA) Snake\nB) Programming language\nReply: A or B",
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.message.reply_text(
                "🧠 Quiz stub: type <code>start</code> to begin.",
                parse_mode=ParseMode.HTML,
            )
        return

    if mode == MODE_TALK:
        persona = context.user_data.get("persona", "friendly_mentor")
        await update.message.reply_text(
            f"🎭 <b>Talk stub</b> ({persona})\nYou said: <code>{safe_text}</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    context.user_data["mode"] = MODE_GPT
    await update.message.reply_text(
        "⚠️ Unknown mode. Switching to <b>GPT mode</b>.",
        parse_mode=ParseMode.HTML,
    )


def run():
    app = ApplicationBuilder().token(TG_BOT_API_KEY).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gpt", set_gpt_mode))
    app.add_handler(CommandHandler("random", set_random_mode))
    app.add_handler(CommandHandler("quiz", set_quiz_mode))
    app.add_handler(CommandHandler("talk", set_talk_mode))
    app.add_handler(CommandHandler("reset", reset))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()


if __name__ == '__main__':
    run()
