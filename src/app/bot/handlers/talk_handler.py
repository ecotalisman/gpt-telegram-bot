import html
from telegram import Update
from telegram.ext import ContextTypes

from app.bot.message_sender import send_html_message


async def handle_talk_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> None:
    """Handle Talk mode message (stub for now)"""
    persona = context.user_data.get("persona", "friendly_mentor")
    safe_text = html.escape(user_text)
    safe_persona = html.escape(persona)

    await send_html_message(
        update,
        context,
        f"🎭 <b>Talk stub</b> ({safe_persona})\nYou said: <code>{safe_text}</code>",
    )
