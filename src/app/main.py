import asyncio

from app.db.database import init_db
from app.bot.bot import run


def main() -> None:
    asyncio.run(init_db())
    run()


if __name__ == "__main__":
    main()
