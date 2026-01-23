from __future__ import annotations

import logging

from openai import OpenAIError
from telegram import Update
from telegram.ext import ContextTypes

from src.app.bot.keyboards import (
    get_button,
    get_talk_personas,
    talk_chat_keyboard,
    talk_persona_keyboard,
    main_keyboard,
)
from src.app.bot.message_sender import send_html_message
from src.app.bot.resource_loader import load_prompt
from src.app.db.enums import MessageRole, SessionMode
from src.app.db.repository import GptThreadRepository
from src.app.services.openai_client import OpenAIClient
from src.app.settings.config import settings

logger = logging.getLogger(__name__)


def _uid(update: Update) -> int | str:
    return update.effective_user.id if update.effective_user else "unknown"


async def handle_talk_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> None:
    if not update.effective_user:
        logger.warning("No effective_user in talk handler")
        await send_html_message(update, context, "Could not identify user.")
        return

    tg_user_id = update.effective_user.id
    text = (user_text or "").strip()

    finish_text = get_button("finish")
    talk_personas = get_talk_personas()

    if text == finish_text:
        logger.info("Talk finished by user=%s (button)", tg_user_id)
        context.user_data["mode"] = SessionMode.GPT.value
        await send_html_message(
            update,
            context,
            "✅ Talk finished. Back to <b>GPT</b>.",
            reply_markup=main_keyboard(),
        )
        return

    # Persona selection
    if text in talk_personas:
        context.user_data["persona_name"] = text
        logger.info("Talk persona selected user=%s persona=%s", tg_user_id, text)

        # Reset talk session so the new persona starts clean
        repo: GptThreadRepository = context.bot_data["thread_repository"]
        await repo.reset_mode(tg_user_id, SessionMode.TALK.value)

        await send_html_message(
            update,
            context,
            f"Persona set to <b>{text}</b>. Now write a message:",
            reply_markup=talk_chat_keyboard(),
        )
        return

    # Regular chat message
    client: OpenAIClient = context.bot_data["openai_client"]
    repo: GptThreadRepository = context.bot_data["thread_repository"]

    mode = SessionMode.TALK.value
    conversation_id, last_response_id = await repo.get_or_create_session(tg_user_id, mode)

    persona_name = context.user_data.get("persona_name") or next(iter(talk_personas.keys()))
    persona_prompt = talk_personas.get(persona_name, "")

    system_prompt = load_prompt("talk") + "\n\nPersona:\n" + persona_prompt

    await repo.add_message(conversation_id, MessageRole.USER.value, text)

    logger.debug("Talk ask user=%s persona=%s prev_response_id=%s", tg_user_id, persona_name, last_response_id)

    try:
        result = await client.ask(
            user_message=text,
            system_prompt=system_prompt,
            model=settings.openai_model,
            previous_response_id=last_response_id,
        )
    except OpenAIError:
        logger.exception("OpenAIError on talk ask (user=%s)", tg_user_id)
        await send_html_message(update, context, "OpenAI error. Try again later.")
        return

    await repo.set_last_response_id(tg_user_id, mode, result.response_id)
    await repo.add_message(conversation_id, MessageRole.ASSISTANT.value, result.text)

    logger.info("Talk response user=%s persona=%s chars=%s", tg_user_id, persona_name, len(result.text))

    await send_html_message(update, context, result.text, reply_markup=talk_chat_keyboard())
