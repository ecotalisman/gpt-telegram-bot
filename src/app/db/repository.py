from __future__ import annotations

import uuid
from typing import Optional, Tuple

import aiosqlite

from app.db.database import get_db_path


class GptThreadRepository:
    """Repository for conversation sessions + local message history (SQLite)."""

    async def get_session(self, tg_user_id: int, mode: str) -> Optional[Tuple[str, Optional[str]]]:
        """
        Returns (conversation_id, last_response_id) or None
        """
        async with aiosqlite.connect(get_db_path()) as db:
            cur = await db.execute(
                "SELECT conversation_id, last_response_id FROM user_threads WHERE tg_user_id=? AND mode=?;",
                (tg_user_id, mode),
            )
            row = await cur.fetchone()
            return (row[0], row[1]) if row else None

    async def get_or_create_session(self, tg_user_id: int, mode: str) -> Tuple[str, Optional[str]]:
        session = await self.get_session(tg_user_id, mode)
        if session:
            return session

        conversation_id = f"conv_{uuid.uuid4().hex}"
        await self.upsert_session(tg_user_id, mode, conversation_id, last_response_id=None)
        return conversation_id, None

    async def upsert_session(
        self,
        tg_user_id: int,
        mode: str,
        conversation_id: str,
        last_response_id: Optional[str],
    ) -> None:
        async with aiosqlite.connect(get_db_path()) as db:
            await db.execute(
                """
                INSERT INTO user_threads (tg_user_id, mode, conversation_id, last_response_id)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(tg_user_id, mode)
                DO UPDATE SET conversation_id=excluded.conversation_id, last_response_id=excluded.last_response_id;
                """,
                (tg_user_id, mode, conversation_id, last_response_id),
            )
            await db.commit()

    async def set_last_response_id(self, tg_user_id: int, mode: str, last_response_id: Optional[str]) -> None:
        async with aiosqlite.connect(get_db_path()) as db:
            await db.execute(
                """
                UPDATE user_threads
                SET last_response_id = ?
                WHERE tg_user_id = ? AND mode = ?;
                """,
                (last_response_id, tg_user_id, mode),
            )
            await db.commit()

    async def add_message(self, conversation_id: str, role: str, content: str) -> None:
        async with aiosqlite.connect(get_db_path()) as db:
            await db.execute(
                """
                INSERT INTO thread_messages (conversation_id, role, content)
                VALUES (?, ?, ?);
                """,
                (conversation_id, role, content),
            )
            await db.commit()

    async def reset_mode(self, tg_user_id: int, mode: str) -> None:
        session = await self.get_session(tg_user_id, mode)
        if not session:
            return
        conversation_id, _ = session

        async with aiosqlite.connect(get_db_path()) as db:
            await db.execute("DELETE FROM user_threads WHERE tg_user_id=? AND mode=?;", (tg_user_id, mode))
            await db.execute("DELETE FROM thread_messages WHERE conversation_id=?;", (conversation_id,))
            await db.commit()

    async def reset_user(self, tg_user_id: int) -> None:
        async with aiosqlite.connect(get_db_path()) as db:
            # get all conversation_ids
            cur = await db.execute("SELECT conversation_id FROM user_threads WHERE tg_user_id=?;", (tg_user_id,))
            rows = await cur.fetchall()
            conv_ids = [r[0] for r in rows]

            await db.execute("DELETE FROM user_threads WHERE tg_user_id=?;", (tg_user_id,))
            for cid in conv_ids:
                await db.execute("DELETE FROM thread_messages WHERE conversation_id=?;", (cid,))
            await db.commit()
