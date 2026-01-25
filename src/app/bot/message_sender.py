from __future__ import annotations

import logging
from pathlib import Path

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import TimedOut, NetworkError
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _msg(update: Update):
    return update.effective_message


async def send_html_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
) -> None:
    msg = _msg(update)
    if not msg:
        logger.warning("No message object available for reply (update=%s)", type(update))
        return

    try:
        await msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    except Exception:
        logger.exception("Failed to send HTML message; retrying without ParseMode.HTML")
        try:
            await msg.reply_text(text, reply_markup=reply_markup)
        except Exception:
            logger.exception("Failed to send plain text message as fallback")


async def send_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    image_path: str | Path,
    caption: str = "",
    reply_markup=None,
) -> None:
    msg = _msg(update)
    if not msg:
        logger.warning("No message object available for photo reply (update=%s)", type(update))
        return

    path = Path(image_path)
    if not path.exists():
        logger.warning("Image not found: %s", path)
        await send_html_message(
            update,
            context,
            f"⚠️ Image not found: <code>{path}</code>",
            reply_markup=reply_markup,
        )
        return

    try:
        with path.open("rb") as f:
            await msg.reply_photo(
                photo=f,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30,
            )
    except (TimedOut, NetworkError) as e:
        logger.warning("Photo upload timed out (%s), falling back to text: %s", path, e)
        await send_html_message(update, context, caption, reply_markup=reply_markup)
    except Exception:
        logger.exception("Failed to send photo: %s", path)
        await send_html_message(update, context, caption, reply_markup=reply_markup)
