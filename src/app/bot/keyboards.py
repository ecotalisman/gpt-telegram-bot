from telegram import ReplyKeyboardMarkup, KeyboardButton

BUTTON_FINISH = "Finish"
BUTTON_ANOTHER_FACT = "I want another fact"
BUTTON_ANOTHER_QUESTION = "Another question"
BUTTON_CHANGE_TOPIC = "Change topic"

QUIZZ_TOPICS = ["Python", "JavaScript", "Docker", "Web"]
TALK_PERSONAS = {
    "Ada Lovelace": "You are Ada Lovelace, poetic and visionary about computing.",
    "Albert Einstein": "You are Albert Einstein, thoughtful, curious, and explains ideas simply.",
    "Elon Musk": "You are Elon Musk, concise and pragmatic with a bold tone.",
}


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("/gpt"), KeyboardButton("/random"), KeyboardButton("/quiz"), KeyboardButton("/talk")],
            [KeyboardButton("/start"), KeyboardButton("/reset")],
        ],
        resize_keyboard=True,
    )


def talk_persona_keyboard() -> ReplyKeyboardMarkup:
    names = list(TALK_PERSONAS.keys())
    rows = []
    for i in range(0, len(names), 2):
        rows.append([KeyboardButton(n) for n in names[i:i + 2]])
    rows.append([KeyboardButton(BUTTON_FINISH)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def talk_chat_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[KeyboardButton(BUTTON_FINISH)]], resize_keyboard=True)


def quiz_topic_keyboard() -> ReplyKeyboardMarkup:
    rows = [QUIZZ_TOPICS, [BUTTON_FINISH]]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def quiz_action_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BUTTON_ANOTHER_QUESTION), KeyboardButton(BUTTON_CHANGE_TOPIC)],
            [KeyboardButton(BUTTON_FINISH)],
        ],
        resize_keyboard=True,
    )
