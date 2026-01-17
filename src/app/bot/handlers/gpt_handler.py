import html
from telegram import Update
from telegram.ext import ContextTypes

from app.bot.message_sender import send_html_message


async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> None:
    """Handle GPT mode message (stub for now)"""
    safe = html.escape(user_text)
    await send_html_message(
        update,
        context,
        f"🤖 <b>GPT stub</b>\nYou wrote: <code>{safe}</code>",
    )
