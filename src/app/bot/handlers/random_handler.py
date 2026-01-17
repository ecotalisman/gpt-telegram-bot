from telegram import Update
from telegram.ext import ContextTypes

from app.bot.message_sender import send_html_message


async def handle_random_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Random mode message (stub for now)"""
    await send_html_message(
        update,
        context,
        "🎲 <b>Random fact stub</b>\nDid you know? The first computer bug was an actual moth 🦋"
    )
