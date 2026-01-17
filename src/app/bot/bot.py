from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.settings.config import settings
from app.bot import commands
from app.bot.handlers.message_router import route_text


def run():
    app = ApplicationBuilder().token(settings.tg_bot_api_key).build()
    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("gpt", commands.set_gpt_mode))
    app.add_handler(CommandHandler("random", commands.set_random_mode))
    app.add_handler(CommandHandler("quiz", commands.set_quiz_mode))
    app.add_handler(CommandHandler("talk", commands.set_talk_mode))
    app.add_handler(CommandHandler("reset", commands.reset))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text))

    app.run_polling()
