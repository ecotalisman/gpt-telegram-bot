import aiosqlite
from pathlib import Path
from typing import Optional
from app.settings.config import settings

def get_db_path() -> Path:
    """
    Return path to the SQLite database file: <project_root>/storage/bot.db
    """
    # database.py -> db -> app -> src -> project_root
    storage_dir = settings.project_root / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)

    return storage_dir / "bot.db"


async def init_db() -> None:
    """
    Initialize DB schema.

    user_state:
      - tg_user_id: Telegram user id (primary key)
      - mode: current bot mode (gpt/random/talk/quiz)

    user_threads:
      - (tg_user_id, mode) is primary key
      - thread_id: OpenAI thread per user per mode
    """
    db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        # Better concurrency for frequent reads/writes
        await db.execute("PRAGMA journal_mode=WAL;")

        # Current mode per user
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_state (
                tg_user_id INTEGER PRIMARY KEY,
                mode TEXT NOT NULL
            );
            """
        )

        # Thread per user per mode
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_threads (
                tg_user_id INTEGER NOT NULL,
                mode TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                PRIMARY KEY (tg_user_id, mode)
            ) 
            """
        )
        await db.commit()


async def get_mode(tg_user_id: int, default: str) -> str:
    """Return saved mode for user or `default` if user doesn't exist yet."""
    async with aiosqlite.connect(get_db_path()) as db:
        cursor = await db.execute(
            "SELECT mode FROM user_state WHERE tg_user_id = ?;",
            (tg_user_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else default


async def set_mode(tg_user_id: int, mode: str) -> None:
    """Upsert mode for user."""
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute(
            """
            INSERT INTO user_state (tg_user_id, mode)
            VALUES (?, ?)
            ON CONFLICT(tg_user_id) DO UPDATE SET mode = excluded.mode;
            """,
            (tg_user_id, mode),
        )
        await db.commit()


async def get_thread_id(tg_user_id: int, mode: str) -> Optional[str]:
    """Return saved OpenAI thread_id for user+mode (or None)"""
    async with aiosqlite.connect(get_db_path()) as db:
        cursor = await db.execute(
            "SELECT thread_id FROM user_threads WHERE tg_user_id = ? AND mode = ?;",
            (tg_user_id, mode),
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def set_thread_id(tg_user_id: int, mode: str, thread_id: str) -> None:
    """Upsert OpenAI thread_id for user+mode"""
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute(
            """
            INSERT INTO user_threads (tg_user_id, mode, thread_id)
            VALUES (?, ?, ?)
            ON CONFLICT(tg_user_id, mode) DO UPDATE SET thread_id = excluded.thread_id;
            """,
            (tg_user_id, mode, thread_id),
        )
        await db.commit()
