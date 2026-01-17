from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import main_keyboard
from app.bot.message_sender import send_html_message
from app.bot.resource_loader import load_message

MODE_GPT = "gpt"
MODE_RANDOM = "random"
MODE_QUIZ = "quiz"
MODE_TALK = "talk"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show main message and set default mode to GPT."""
    text = load_message("main")
    context.user_data["mode"] = MODE_GPT
    await send_html_message(update, context, text, reply_markup=main_keyboard(),)


async def set_gpt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to GPT mode"""
    context.user_data["mode"] = MODE_GPT
    await send_html_message(
        update,
        context,
        "✅ <b>GPT mode</b> enabled.\nWrite your question:",
        reply_markup=main_keyboard(),
    )


async def set_random_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to Random mode"""
    context.user_data["mode"] = MODE_RANDOM
    await send_html_message(
        update,
        context,
        "✅ <b>Random facts mode</b> enabled.\nSend any message and I’ll reply with a fact (stub for now).",
        reply_markup=main_keyboard(),
    )


async def set_quiz_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to Quiz mode"""
    context.user_data["mode"] = MODE_QUIZ
    await send_html_message(
        update,
        context,
        "✅ <b>Quiz mode</b> enabled.\nSend 'start' to begin (stub for now).",
        reply_markup=main_keyboard(),
    )


async def set_talk_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to Talk mode"""
    context.user_data["mode"] = MODE_TALK
    context.user_data["persona"] = "friendly_mentor"
    await send_html_message(
        update,
        context,
        "🎭 <b>Talk mode</b> enabled.\nNow I’ll reply as your persona (stub).\nWrite something:",
        reply_markup=main_keyboard(),
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear user state and go back to GPT"""
    context.user_data.clear()
    context.user_data["mode"] = MODE_GPT
    await send_html_message(
        update,
        context,
        "♻️ Reset done. Back to <b>GPT mode</b>.",
        reply_markup=main_keyboard(),
    )
