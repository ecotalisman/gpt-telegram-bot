from __future__ import annotations

import logging

from openai import OpenAIError
from telegram import Update
from telegram.ext import ContextTypes

from src.app.bot.message_sender import send_html_message
from src.app.bot.resource_loader import load_prompt
from src.app.db.enums import MessageRole, SessionMode
from src.app.db.repository import GptThreadRepository
from src.app.services.openai_client import OpenAIClient
from src.app.settings.config import settings

logger = logging.getLogger(__name__)


async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> None:
    if not update.effective_user:
        logger.warning("No effective_user in update")
        await send_html_message(update, context, "⚠️ Could not identify user.")
        return

    tg_user_id = update.effective_user.id
    mode = SessionMode.GPT.value

    client: OpenAIClient = context.bot_data["openai_client"]
    repo: GptThreadRepository = context.bot_data["thread_repository"]

    conversation_id, last_response_id = await repo.get_or_create_session(tg_user_id, mode)
    system_prompt = load_prompt("gpt")

    await repo.add_message(conversation_id, MessageRole.USER.value, user_text)

    async def _ask(previous_response_id):
        return await client.ask(
            user_message=user_text,
            system_prompt=system_prompt,
            model=settings.openai_model,
            previous_response_id=previous_response_id,
        )

    try:
        logger.debug("GPT ask user=%s mode=%s prev_response_id=%s", tg_user_id, mode, last_response_id)
        result = await _ask(last_response_id)
    except OpenAIError:
        logger.exception("OpenAIError on GPT ask; resetting continuation and retrying once (user=%s)", tg_user_id)
        try:
            await repo.set_last_response_id(tg_user_id, mode, None)
            result = await _ask(None)
        except OpenAIError:
            logger.exception("OpenAIError on GPT retry (user=%s)", tg_user_id)
            await send_html_message(update, context, "⚠️ OpenAI error. Try again a bit later.")
            return

    await repo.set_last_response_id(tg_user_id, mode, result.response_id)
    await repo.add_message(conversation_id, MessageRole.ASSISTANT.value, result.text)

    await send_html_message(update, context, result.text)
