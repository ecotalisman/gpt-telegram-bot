from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from openai import AsyncOpenAI, OpenAIError
from app.settings.config import settings


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
        try:
            response = await self._client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                previous_response_id=previous_response_id,
            )

            # SDK provides a helper that concatenates text output
            text = (getattr(response, "output_text", "") or "").strip()
            if not text:
                text = "⚠️ No assistant text returned"

            return AskResult(text=text, response_id=response.id)

        except OpenAIError:
            # Re-raise so caller can handle (show error in Telegram, retry, log, etc.)
            raise
