from __future__ import annotations

import logging
import asyncio
from dataclasses import dataclass
from typing import Optional

from openai import AsyncOpenAI, OpenAIError, RateLimitError, APIStatusError
from src.app.settings.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AskResult:
    """Result of one model call (text + id to continue conversation"""
    text: str
    response_id: str


class OpenAIClient:
    """
    OpenAI wrapper using the Responses API (recommended)
    - No beta threads/runs => no deprecated warnings
    - Conversation is continued via previous_response_id
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def ask(
            self,
            user_message: str,
            system_prompt: str,
            *,
            model: str = "gpt-4o-mini",
            previous_response_id: Optional[str] = None,
    ) -> AskResult:
        """
        Send one user message and get one assistant reply

        Args:
            user_message: text from Telegram user
            system_prompt: your "prompt file" (gpt.txt / random.txt, talk.txt / quiz.txt)
            model: model name
            previous_response_id: if provided, continues the conversation

        Returns:
            AskResult(text=..., response_id=...)
        """
        MAX_RETRIES = 3
        RETRY_DELAY = 1.0

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.debug(f"OpenAI request attempt {attempt}/{MAX_RETRIES}")

                response = await self._client.responses.create(
                    model=model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    previous_response_id=previous_response_id,
                )

                text = (getattr(response, "output_text", "") or "").strip()
                if not text:
                    text = "⚠️ No assistant text returned"

                logger.info(f"OpenAI response received: {len(text)} chars")
                return AskResult(text=text, response_id=response.id)

            except RateLimitError as e:
                logger.warning(f"Rate limit hit, attempt {attempt}/{MAX_RETRIES}: {e}")
                if attempt == MAX_RETRIES:
                    raise
                await asyncio.sleep(RETRY_DELAY * attempt)

            except APIStatusError as e:
                if e.status_code >= 500:
                    logger.warning(f"Server error, attempt {attempt}/{MAX_RETRIES}: {e}")
                    if attempt == MAX_RETRIES:
                        raise
                    await asyncio.sleep(RETRY_DELAY * attempt)
                else:
                    logger.error(f"OpenAI API error: {e}")
                    raise

            except OpenAIError as e:
                logger.error(f"OpenAI error: {e}")
                raise
