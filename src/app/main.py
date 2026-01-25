import asyncio
import logging

from src.app.bot.bot import run
from src.app.db.database import init_db
from src.app.settings.logging_config import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    logger.info("Starting GPT Telegram Bot...")

    try:
        asyncio.run(init_db())
        run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception:
        logger.critical("Bot crashed", exc_info=True)
        raise


if __name__ == "__main__":
    main()
