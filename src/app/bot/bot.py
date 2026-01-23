import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.app.settings.config import settings
from src.app.bot import commands
from src.app.bot.handlers.message_router import route_text

from src.app.db.repository import GptThreadRepository
from src.app.services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


def run():
    logger.info("Starting Telegram bot...")

    try:
        app = ApplicationBuilder().token(settings.tg_bot_api_key).build()

        app.bot_data["openai_client"] = OpenAIClient()
        app.bot_data["thread_repository"] = GptThreadRepository()

        # Register handlers
        app.add_handler(CommandHandler("start", commands.start))
        app.add_handler(CommandHandler("gpt", commands.set_gpt_mode))
        app.add_handler(CommandHandler("random", commands.set_random_mode))
        app.add_handler(CommandHandler("quiz", commands.set_quiz_mode))
        app.add_handler(CommandHandler("talk", commands.set_talk_mode))
        app.add_handler(CommandHandler("reset", commands.reset))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text))

        logger.info("Bot handlers registered, starting polling...")
        app.run_polling()

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
    finally:
        logger.info("Bot stopped")
