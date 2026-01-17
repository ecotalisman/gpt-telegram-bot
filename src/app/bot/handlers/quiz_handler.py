from telegram import Update
from telegram.ext import ContextTypes

from app.bot.message_sender import send_html_message


async def handle_quiz_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> None:
    """Handle Quiz mode message (stub for now)"""
    if user_text.lower() == "start":
        await send_html_message(
            update,
            context,
            "🧠 <b>Quiz stub</b>\nQ1: What is Python?\nA) Snake\nB) Programming language\nReply: A or B",
        )
        return

    await send_html_message(
        update,
        context,
        "🧠 Quiz stub: type <code>start</code> to begin",
    )
