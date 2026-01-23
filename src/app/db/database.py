from __future__ import annotations

import logging
import aiosqlite
from pathlib import Path
from src.app.settings.config import settings

logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """
    Return path to the SQLite database file: <project_root>/storage/bot.db
    """
    storage_dir = settings.project_root / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)

    return storage_dir / "bot.db"


async def init_db() -> None:
    """
    Creates DB schema for conversation sessions (Responses API):

    - user_threads: one session per (tg_user_id, mode)
      stores:
        - conversation_id: our stable conversation key
        - last_response_id: last OpenAI response id to continue context via Responses API

    - thread_messages: local history copy linked by conversation_id
    """
    db_path = get_db_path()
    logger.info(f"Initializing database at {db_path}")

    try:
        async with aiosqlite.connect(db_path) as db:
            # Better concurrency for frequent reads/writes
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA busy_timeout=5000;")
            await db.execute("PRAGMA foreign_keys=ON;")

            # Session per (tg_user_id, mode)
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_threads
                (
                    tg_user_id INTEGER NOT NULL,
                    mode TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    last_response_id TEXT,
                    PRIMARY KEY
                        (
                            tg_user_id,
                            mode
                        )
                );
                """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS thread_messages
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_thread_messages_conversation
                    ON thread_messages(conversation_id);
                """
            )
            await db.commit()
        logger.info("Database initialized successfully")
    except aiosqlite.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise
