from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.app.bot.keyboards import main_keyboard, quiz_topic_keyboard, talk_persona_keyboard
from src.app.bot.message_sender import send_html_message
from src.app.bot.resource_loader import load_message
from src.app.db.enums import SessionMode
from src.app.db.repository import GptThreadRepository

logger = logging.getLogger(__name__)


def _user_id(update: Update) -> int | str:
    return update.effective_user.id if update.effective_user else "unknown"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = _user_id(update)
    logger.info("User %s executed /start", uid)

    text = load_message("main")
    context.user_data["mode"] = SessionMode.GPT.value

    await send_html_message(update, context, text, reply_markup=main_keyboard())


async def set_gpt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = _user_id(update)
    logger.info("User %s executed /gpt", uid)

    context.user_data["mode"] = SessionMode.GPT.value
    await send_html_message(
        update,
        context,
        "✅ <b>GPT mode</b> enabled.\nWrite your question:",
        reply_markup=main_keyboard(),
    )


async def set_random_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = _user_id(update)
    logger.info("User %s executed /random", uid)

    context.user_data["mode"] = SessionMode.RANDOM.value
    await send_html_message(
        update,
        context,
        "✅ <b>Random facts mode</b> enabled.\nSend any text (optional topic).",
        reply_markup=main_keyboard(),
    )


async def set_quiz_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = _user_id(update)
    logger.info("User %s executed /quiz", uid)

    context.user_data["mode"] = SessionMode.QUIZ.value
    context.user_data["quiz_state"] = "choose_topic"

    await send_html_message(
        update,
        context,
        "🧠 <b>Quiz mode</b>\nChoose a topic:",
        reply_markup=quiz_topic_keyboard(),
    )


async def set_talk_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = _user_id(update)
    logger.info("User %s executed /talk", uid)

    context.user_data["mode"] = SessionMode.TALK.value
    context.user_data.pop("persona_name", None)

    await send_html_message(
        update,
        context,
        "🎭 <b>Talk mode</b> enabled.\nChoose a persona:",
        reply_markup=talk_persona_keyboard(),
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = _user_id(update)
    logger.info("User %s executed /reset", uid)

    context.user_data.clear()
    context.user_data["mode"] = SessionMode.GPT.value

    thread_reset_ok = True
    repo: GptThreadRepository | None = context.bot_data.get("thread_repository")

    if not repo or not update.effective_user:
        thread_reset_ok = False
        logger.warning(
            "Cannot reset threads (repo=%s, effective_user=%s) for user %s",
            bool(repo),
            bool(update.effective_user),
            uid,
        )
    else:
        try:
            result = await repo.reset_user(update.effective_user.id)
            if result is False:
                thread_reset_ok = False
                logger.warning("reset_user returned False for user %s", uid)
            else:
                logger.info("Threads reset for user %s", uid)
        except Exception:
            thread_reset_ok = False
            logger.exception("Failed to reset threads for user %s", uid)

    msg = "♻️ Reset done. Back to <b>GPT mode</b>."
    if not thread_reset_ok:
        msg += "\n⚠️ Note: thread cleanup was not fully successful (see logs)."

    await send_html_message(update, context, msg, reply_markup=main_keyboard())
