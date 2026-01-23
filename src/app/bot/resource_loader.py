from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from src.app.settings.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def load_message(name: str) -> str:
    path = settings.messages_dir / f"{name}.txt"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error("Message file not found: %s", path)
        raise


@lru_cache(maxsize=32)
def load_prompt(name: str) -> str:
    path = settings.prompts_dir / f"{name}.txt"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error("Prompt file not found: %s", path)
        raise


def image_path(name: str) -> str:
    path: Path = settings.resources_dir / "images" / f"{name}.png"
    if not path.exists():
        logger.warning("Image file not found: %s", path)
    return str(path)
