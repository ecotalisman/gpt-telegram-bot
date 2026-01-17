from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


async def send_html_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None) -> None:
    """Send a message with HTML parse mode"""
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, image_path: str, caption: str = "", reply_markup=None) -> None:
    """Send a photo from local path with optional caption"""
    await update.message.reply_photo(
        photo=image_path,
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )