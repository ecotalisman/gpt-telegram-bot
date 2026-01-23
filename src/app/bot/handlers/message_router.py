from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.app.bot.handlers.gpt_handler import handle_gpt_message
from src.app.bot.handlers.quiz_handler import handle_quiz_message
from src.app.bot.handlers.random_handler import handle_random_message
from src.app.bot.handlers.talk_handler import handle_talk_message
from src.app.bot.message_sender import send_html_message
from src.app.db.enums import SessionMode

logger = logging.getLogger(__name__)


def _user_id(update: Update) -> int | str:
    return update.effective_user.id if update.effective_user else "unknown"


async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        logger.warning("Received update without effective_message (user=%s)", _user_id(update))
        return

    user_text = (update.effective_message.text or "").strip()
    mode = context.user_data.get("mode", SessionMode.GPT.value)
    uid = _user_id(update)

    logger.debug("Routing message from user=%s mode=%s text_len=%s", uid, mode, len(user_text))

    if mode == SessionMode.RANDOM.value:
        await handle_random_message(update, context, user_text)
        return

    if mode == SessionMode.GPT.value:
        await handle_gpt_message(update, context, user_text)
        return

    if mode == SessionMode.QUIZ.value:
        await handle_quiz_message(update, context, user_text)
        return

    if mode == SessionMode.TALK.value:
        await handle_talk_message(update, context, user_text)
        return

    logger.warning("Unknown mode=%s for user=%s. Switching to GPT.", mode, uid)
    context.user_data["mode"] = SessionMode.GPT.value
    await send_html_message(update, context, "⚠️ Unknown mode. Switching to <b>GPT mode</b>.")
