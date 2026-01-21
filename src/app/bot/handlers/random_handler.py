from openai import OpenAIError
from telegram import Update
from telegram.ext import ContextTypes

from app.settings.config import settings
from app.bot.message_sender import send_html_message
from app.bot.resource_loader import load_prompt
from app.db.enums import MessageRole, SessionMode
from app.db.repository import GptThreadRepository
from app.services.openai_client import OpenAIClient


async def handle_random_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> None:
    client: OpenAIClient = context.bot_data["openai_client"]
    repo: GptThreadRepository = context.bot_data["thread_repository"]

    tg_user_id = update.effective_user.id if update.effective_user else 0
    mode = SessionMode.RANDOM.value

    conversation_id, last_response_id = await repo.get_or_create_session(tg_user_id, mode)
    system_prompt = load_prompt("random")

    # If user wrote a topic, use it. Otherwise, ask for any fact.
    topic = (user_text or "").strip()
    if topic:
        user_message = f"Give ONE surprising technical/science fact related to: {topic}"
    else:
        user_message = "Give ONE surprising technical/science fact."

    await repo.add_message(conversation_id, MessageRole.USER.value, user_message)

    try:
        result = await client.ask(
            user_message=user_message,
            system_prompt=system_prompt,
            model=settings.openai_model,
            previous_response_id=last_response_id,
        )
    except OpenAIError:
        await send_html_message(update, context, "⚠️ OpenAI error. Try again later.")
        return

    await repo.set_last_response_id(tg_user_id, mode, result.response_id)
    await repo.add_message(conversation_id, MessageRole.ASSISTANT.value, result.text)
    await send_html_message(update, context, result.text)
