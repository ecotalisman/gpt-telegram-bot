import aiosqlite
from pathlib import Path
from typing import Optional


def get_db_path() -> Path:
    """
    Return path to the SQLite database file: <project_root>/storage/bot.db.

    We intentionally store DB outside of src/ so:
    - it doesn't get mixed with source code
    - it works regardless of the current working directory (CWD)
    """
    # database.py -> db -> app -> src -> project_root
    project_root = Path(__file__).resolve().parents[3]

    storage_dir = project_root / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)

    return storage_dir / "bot.db"


async def init_db() -> None:
    """
    Initialize DB schema.

    user_state stores per-user state:
      - tg_user_id: Telegram user id (primary key)
      - mode: current bot mode (gpt/random/quiz)
      - thread_id: OpenAI thread id (will be used later)
    """
    db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        # WAL improves concurrency for frequent reads/writes
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_state (
                tg_user_id INTEGER PRIMARY KEY,
                mode TEXT NOT NULL,
                thread_id TEXT
            );
            """
        )
        await db.commit()


async def get_mode(tg_user_id: int, default: str) -> str:
    """Return saved mode for user or `default` if user doesn't exist yet."""
    db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT mode FROM user_state WHERE tg_user_id = ?;",
            (tg_user_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else default


async def set_mode(tg_user_id: int, mode: str) -> None:
    """Upsert mode for user."""
    db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            INSERT INTO user_state (tg_user_id, mode, thread_id)
            VALUES (?, ?, NULL) ON CONFLICT(tg_user_id) DO
            UPDATE SET mode = excluded.mode;
            """,
            (tg_user_id, mode),
        )
        await db.commit()


async def get_thread_id(tg_user_id: int) -> Optional[str]:
    """Return saved OpenAI thread_id for user (or None)."""
    db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT thread_id FROM user_state WHERE tg_user_id = ?;",
            (tg_user_id,),
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def set_tgread_id(tg_user_id: int, thread_id: str) -> None:
    """Upsert OpenAI thread_id for user."""
    db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            INSERT INTO user_state (tg_user_id, mode, thread_id)
            VALUES (?, 'gpt', ?) ON CONFLICT(tg_user_id) DO
            UPDATE SET thread_id = excluded.thread_id;
            """,
            (tg_user_id, thread_id),
        )
        await db.commit()
