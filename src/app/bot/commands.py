from telegram import Update
from telegram.ext import ContextTypes

from app.bot.keyboards import main_keyboard, talk_persona_keyboard
from app.bot.message_sender import send_html_message
from app.bot.resource_loader import load_message

from app.db.repository import GptThreadRepository

MODE_GPT = "gpt"
MODE_RANDOM = "random"
MODE_QUIZ = "quiz"
MODE_TALK = "talk"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = load_message("main")
    context.user_data["mode"] = MODE_GPT
    await send_html_message(update, context, text, reply_markup=main_keyboard())


async def set_gpt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = MODE_GPT
    await send_html_message(update, context, "✅ <b>GPT mode</b> enabled.\nWrite your question:", reply_markup=main_keyboard())


async def set_random_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = MODE_RANDOM
    await send_html_message(update, context, "✅ <b>Random facts mode</b> enabled.\nSend any text (optional topic).", reply_markup=main_keyboard())


async def set_quiz_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = MODE_QUIZ
    await send_html_message(update, context, "✅ <b>Quiz mode</b> enabled.\n(We’ll implement topics next step.)", reply_markup=main_keyboard())


async def set_talk_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["mode"] = MODE_TALK
    context.user_data.pop("persona_name", None)
    await send_html_message(
        update,
        context,
        "🎭 <b>Talk mode</b> enabled.\nChoose a persona:",
        reply_markup=talk_persona_keyboard(),
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data["mode"] = MODE_GPT

    repo: GptThreadRepository | None = context.bot_data.get("thread_repository")
    if repo and update.effective_user:
        await repo.reset_user(update.effective_user.id)

    await send_html_message(update, context, "♻️ Reset done. Back to <b>GPT mode</b>.", reply_markup=main_keyboard())
