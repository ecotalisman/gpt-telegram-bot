from __future__ import annotations

import json
from functools import lru_cache

from telegram import KeyboardButton, ReplyKeyboardMarkup

from src.app.settings.config import settings


@lru_cache(maxsize=1)
def _load_keyboard_config() -> dict:
    config_path = settings.resources_dir / "menus" / "keyboards.json"
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def get_button(key: str) -> str:
    return _load_keyboard_config()["buttons"][key]


def get_quiz_topics() -> list[str]:
    return _load_keyboard_config()["quiz_topics"]


def get_talk_personas() -> dict[str, str]:
    return _load_keyboard_config()["talk_personas"]


# Backward-compatible exports (if other modules still import these names)
BUTTON_FINISH = get_button("finish")
BUTTON_ANOTHER_FACT = get_button("another_fact")
BUTTON_ANOTHER_QUESTION = get_button("another_question")
BUTTON_CHANGE_TOPIC = get_button("change_topic")

QUIZZ_TOPICS = get_quiz_topics()
TALK_PERSONAS = get_talk_personas()


def _chunk_buttons(items: list[str], per_row: int) -> list[list[KeyboardButton]]:
    return [
        [KeyboardButton(x) for x in items[i : i + per_row]]
        for i in range(0, len(items), per_row)
    ]


@lru_cache(maxsize=1)
def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton("/gpt"),
                KeyboardButton("/random"),
                KeyboardButton("/quiz"),
                KeyboardButton("/talk"),
            ],
            [KeyboardButton("/start"), KeyboardButton("/reset")],
        ],
        resize_keyboard=True,
    )


@lru_cache(maxsize=1)
def talk_persona_keyboard() -> ReplyKeyboardMarkup:
    names = list(get_talk_personas().keys())
    rows = _chunk_buttons(names, per_row=2)
    rows.append([KeyboardButton(get_button("finish"))])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


@lru_cache(maxsize=1)
def talk_chat_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton(get_button("finish"))]], resize_keyboard=True)


@lru_cache(maxsize=1)
def quiz_topic_keyboard() -> ReplyKeyboardMarkup:
    topics = get_quiz_topics()
    rows = _chunk_buttons(topics, per_row=2)
    rows.append([KeyboardButton(get_button("finish"))])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def quiz_answer_keyboard(options: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton(o)] for o in options], resize_keyboard=True)


@lru_cache(maxsize=1)
def quiz_action_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(get_button("another_question")),
                KeyboardButton(get_button("change_topic")),
            ],
            [KeyboardButton(get_button("finish"))],
        ],
        resize_keyboard=True,
    )
