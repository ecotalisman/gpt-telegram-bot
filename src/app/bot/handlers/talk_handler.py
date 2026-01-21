from openai import OpenAIError
from telegram import Update
from telegram.ext import ContextTypes

from app.settings.config import settings
from app.bot.keyboards import BUTTON_FINISH, TALK_PERSONAS, talk_chat_keyboard, talk_persona_keyboard
from app.bot.message_sender import send_html_message
from app.bot.resource_loader import load_prompt
from app.db.enums import MessageRole, SessionMode
from app.db.repository import GptThreadRepository
from app.services.openai_client import OpenAIClient


async def handle_talk_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> None:
    if user_text == BUTTON_FINISH:
        context.user_data["mode"] = SessionMode.GPT.value
        await send_html_message(update, context, "✅ Talk finished. Back to <b>GPT</b>.", reply_markup=None)
        return

    # persona selection
    if user_text in TALK_PERSONAS:
        context.user_data["persona_name"] = user_text
        # reset talk session so the new persona starts clean
        repo: GptThreadRepository = context.bot_data["thread_repository"]
        tg_user_id = update.effective_user.id if update.effective_user else 0
        await repo.reset_mode(tg_user_id, SessionMode.TALK.value)

        await send_html_message(
            update,
            context,
            f"🎭 Persona set to <b>{user_text}</b>. Now write a message:",
            reply_markup=talk_chat_keyboard(),
        )
        return

    client: OpenAIClient = context.bot_data["openai_client"]
    repo: GptThreadRepository = context.bot_data["thread_repository"]

    tg_user_id = update.effective_user.id if update.effective_user else 0
    mode = SessionMode.TALK.value

    conversation_id, last_response_id = await repo.get_or_create_session(tg_user_id, mode)

    persona_name = context.user_data.get("persona_name") or next(iter(TALK_PERSONAS.keys()))
    persona_prompt = TALK_PERSONAS.get(persona_name, "")

    system_prompt = load_prompt("talk") + "\n\nPersona:\n" + persona_prompt

    await repo.add_message(conversation_id, MessageRole.USER.value, user_text)

    try:
        result = await client.ask(
            user_message=user_text,
            system_prompt=system_prompt,
            model=settings.openai_model,
            previous_response_id=last_response_id,
        )
    except OpenAIError:
        await send_html_message(update, context, "⚠️ OpenAI error. Try again later.")
        return

    await repo.set_last_response_id(tg_user_id, mode, result.response_id)
    await repo.add_message(conversation_id, MessageRole.ASSISTANT.value, result.text)
    await send_html_message(update, context, result.text, reply_markup=talk_chat_keyboard())
