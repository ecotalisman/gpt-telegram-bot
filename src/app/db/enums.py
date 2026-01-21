from enum import Enum


class SessionMode(str, Enum):
    GPT = "gpt"
    RANDOM = "random"
    QUIZ = "quiz"
    TALK = "talk"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
