from telegram import Update
from telegram.ext import ContextTypes

from app.bot.message_sender import send_html_message
from app.bot.handlers.gpt_handler import handle_gpt_message
from app.bot.handlers.random_handler import handle_random_message
from app.bot.handlers.quiz_handler import handle_quiz_message
from app.bot.handlers.talk_handler import handle_talk_message

MODE_GPT = "gpt"
MODE_RANDOM = "random"
MODE_QUIZ = "quiz"
MODE_TALK = "talk"


async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Route non-command text message depending on current user mode
    """
    user_text = update.message.text.strip()
    if not user_text:
        return
    mode = context.user_data.get("mode", MODE_GPT)

    if mode == MODE_GPT:
        await handle_gpt_message(update, context, user_text)
        return

    if mode == MODE_RANDOM:
        await handle_random_message(update, context)
        return

    if mode == MODE_QUIZ:
        await handle_quiz_message(update, context, user_text)
        return

    if mode == MODE_TALK:
        await handle_talk_message(update, context, user_text)
        return

    context.user_data["mode"] = MODE_GPT
    await send_html_message(
        update,
        context,
        "⚠️ Unknown mode. Switching to <b>GPT mode</b>.",
    )
