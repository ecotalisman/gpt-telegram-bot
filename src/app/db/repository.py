from __future__ import annotations

import logging
import uuid
from typing import Optional, Tuple

import aiosqlite

from src.app.db.database import get_db_path

logger = logging.getLogger(__name__)


class GptThreadRepository:
    """Repository for conversation sessions + local message history (SQLite)."""

    async def get_session(self, tg_user_id: int, mode: str) -> Optional[Tuple[str, Optional[str]]]:
        """Returns (conversation_id, last_response_id) or None"""
        try:
            async with aiosqlite.connect(get_db_path()) as db:
                cur = await db.execute(
                    "SELECT conversation_id, last_response_id FROM user_threads WHERE tg_user_id=? AND mode=?;",
                    (tg_user_id, mode),
                )
                row = await cur.fetchone()
                if row:
                    logger.debug(f"Session found for user {tg_user_id}, mode {mode}")
                return (row[0], row[1]) if row else None
        except aiosqlite.Error as e:
            logger.error(f"Error getting session for user {tg_user_id}: {e}")
            return None

    async def get_or_create_session(self, tg_user_id: int, mode: str) -> Tuple[str, Optional[str]]:
        logger.info("get_or_create_session called: user=%s, mode=%s, db_path=%s", tg_user_id, mode, get_db_path())
        session = await self.get_session(tg_user_id, mode)
        if session:
            logger.info("Existing session found: conv_id=%s, last_resp_id=%s", session[0], session[1])
            return session

        conversation_id = f"conv_{uuid.uuid4().hex}"
        logger.info("Creating NEW session: user=%s, mode=%s, conv_id=%s", tg_user_id, mode, conversation_id)
        await self.upsert_session(tg_user_id, mode, conversation_id, last_response_id=None)
        return conversation_id, None

    async def upsert_session(
        self,
        tg_user_id: int,
        mode: str,
        conversation_id: str,
        last_response_id: Optional[str],
    ) -> None:
        db_path = get_db_path()
        logger.info("[DB] upsert_session: user=%s, mode=%s, conv=%s, path=%s", tg_user_id, mode, conversation_id, db_path.resolve())
        async with aiosqlite.connect(db_path) as db:
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
            logger.info("[DB] upsert_session committed: user=%s, mode=%s", tg_user_id, mode)

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

    async def add_message(self, conversation_id: str, role: str, content: str) -> int:
        logger.info("[DB] Saving message: conv_id=%s, role=%s, content_len=%d chars", conversation_id, role, len(content))
        db_path = get_db_path()
        logger.info("[DB] Using database at: %s", db_path.resolve())
        try:
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute(
                    """
                    INSERT INTO thread_messages (conversation_id, role, content)
                    VALUES (?, ?, ?);
                    """,
                    (conversation_id, role, content),
                )
                await db.commit()
                rowid = cursor.lastrowid
            logger.info("[DB] Message committed successfully: rowid=%s, path=%s", rowid, db_path.resolve())
            return rowid
        except aiosqlite.Error as e:
            logger.error("[DB] Failed to save message: %s", e)
            raise

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
        try:
            async with aiosqlite.connect(get_db_path()) as db:
                cur = await db.execute("SELECT conversation_id FROM user_threads WHERE tg_user_id=?;", (tg_user_id,))
                rows = await cur.fetchall()
                conv_ids = [r[0] for r in rows]

                await db.execute("DELETE FROM user_threads WHERE tg_user_id=?;", (tg_user_id,))

                if conv_ids:
                    placeholders = ",".join("?" * len(conv_ids))
                    await db.execute(f"DELETE FROM thread_messages WHERE conversation_id IN ({placeholders});",
                                     conv_ids)

                await db.commit()
                logger.info(f"User {tg_user_id} data reset: {len(conv_ids)} conversations deleted")
        except aiosqlite.Error as e:
            logger.error(f"Error resetting user {tg_user_id}: {e}")
            raise
