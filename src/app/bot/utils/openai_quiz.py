from __future__ import annotations

import json
import logging
import re
from typing import List, Tuple

from openai import OpenAIError

from src.app.bot.utils.quiz import QuizQuestion
from src.app.services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


def _extract_json_from_response(text: str) -> list:
    """
    Extract and parse JSON array from OpenAI response that may contain markdown.
    Handles various formats: raw JSON, ```json blocks, nested structures.
    """
    original_text = text
    t = (text or "").strip()

    # Remove markdown code blocks (```json ... ``` or ``` ... ```)
    t = re.sub(r"```json\s*\n?", "", t, flags=re.IGNORECASE)
    t = re.sub(r"```\s*\n?", "", t)
    t = t.strip()

    # Try direct parse
    try:
        data = json.loads(t)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "questions" in data:
            return data["questions"]
    except json.JSONDecodeError:
        pass

    # Try to find JSON array [...] using rfind for the last ]
    start = t.find("[")
    end = t.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(t[start : end + 1])
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # Try to find JSON object {...} that might contain questions
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(t[start : end + 1])
            if isinstance(data, dict) and "questions" in data:
                return data["questions"]
        except json.JSONDecodeError:
            pass

    logger.error("Failed to extract JSON from response: %s", original_text[:500])
    raise ValueError("Could not extract valid JSON array from OpenAI response")


def _validate_questions(data) -> List[QuizQuestion]:
    if not isinstance(data, list) or len(data) != 10:
        raise ValueError("Quiz JSON must be an array of exactly 10 items")

    questions: List[QuizQuestion] = []
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Item #{i} must be an object")

        if set(item.keys()) != {"question", "options", "answer"}:
            raise ValueError(f"Item #{i} must have exactly keys: question/options/answer")

        question = item["question"]
        options = item["options"]
        answer = item["answer"]

        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Item #{i} question must be a non-empty string")

        if (
            not isinstance(options, list)
            or len(options) not in (3, 4)
            or not all(isinstance(x, str) and x.strip() for x in options)
        ):
            raise ValueError(f"Item #{i} options must be an array of 3 or 4 non-empty strings")

        if len(set(options)) != len(options):
            raise ValueError(f"Item #{i} options must be unique")

        if not isinstance(answer, str) or answer not in options:
            raise ValueError(f"Item #{i} answer must be exactly one of the options")

        questions.append(
            QuizQuestion(
                question=question.strip(),
                options=[o.strip() for o in options],
                answer=answer.strip(),
            )
        )

    return questions


async def ask_quiz_with_retries(
    *,
    client: OpenAIClient,
    system_prompt: str,
    model: str,
    topic: str,
    previous_response_id: str | None,
    max_attempts: int = 2,
) -> Tuple[List[QuizQuestion], str]:
    """
    Returns (questions, response_id_of_successful_call)
    """
    user_message_base = f'Topic: "{topic}". Generate the quiz now.'
    last_resp_id = previous_response_id

    for attempt in range(1, max_attempts + 1):
        user_message = user_message_base
        if attempt > 1:
            user_message = (
                user_message_base
                + "\n\nIMPORTANT: Your previous output was invalid. Output ONLY a valid JSON array of exactly 10 objects."
            )

        logger.debug(
            "Quiz generation attempt=%s/%s topic=%r prev_response_id=%s",
            attempt,
            max_attempts,
            topic,
            last_resp_id,
        )

        try:
            result = await client.ask(
                user_message=user_message,
                system_prompt=system_prompt,
                model=model,
                previous_response_id=last_resp_id,
            )
        except OpenAIError:
            logger.exception("OpenAIError during quiz generation attempt=%s topic=%r", attempt, topic)
            if attempt == max_attempts:
                raise
            continue

        try:
            data = _extract_json_from_response(result.text)
            questions = _validate_questions(data)
            logger.info("Quiz generation succeeded topic=%r attempt=%s questions=%s", topic, attempt, len(questions))
            return questions, result.response_id
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(
                "Quiz JSON extraction/validation failed topic=%r attempt=%s error=%s response_len=%s",
                topic,
                attempt,
                e,
                len(result.text),
            )

        last_resp_id = result.response_id
        if attempt == max_attempts:
            raise RuntimeError("Quiz generation failed: model returned invalid JSON/questions.")

    raise RuntimeError("Quiz generation failed: unknown error.")
