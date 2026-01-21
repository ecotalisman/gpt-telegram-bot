from __future__ import annotations

from pathlib import Path
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


def _msg(update: Update):
    # works for messages and callback queries
    return update.effective_message


async def send_html_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None) -> None:
    msg = _msg(update)
    if not msg:
        return
    await msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def send_photo(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        image_path: str | Path,
        caption: str = "",
        reply_markup=None,
) -> None:
    msg = _msg(update)
    if not msg:
        return

    path = Path(image_path)
    if not path.exists():
        await send_html_message(update, context, f"⚠️ Image not found: <code>{path}</code>", reply_markup=reply_markup)
        return

    with path.open("rb") as f:
        await msg.reply_photo(photo=f, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup)