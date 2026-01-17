from telegram import ReplyKeyboardMarkup

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
            ["/gpt", "/random", "/quiz", "/talk"],
            ["/start", "/reset"],
        ],
        resize_keyboard=True,
    )


def random_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[BUTTON_ANOTHER_FACT, BUTTON_FINISH]],
        resize_keyboard=True,
    )


def talk_persona_keyboard() -> ReplyKeyboardMarkup:
    rows = [[name] for name in TALK_PERSONAS.keys()]
    rows.append([BUTTON_FINISH])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def talk_chat_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[BUTTON_FINISH]], resize_keyboard=True)


def quiz_topic_keyboard() -> ReplyKeyboardMarkup:
    rows = [[QUIZZ_TOPICS[0], QUIZZ_TOPICS[1], QUIZZ_TOPICS[2], QUIZZ_TOPICS[3]], [BUTTON_FINISH]]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def quiz_action_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[BUTTON_ANOTHER_QUESTION, BUTTON_CHANGE_TOPIC], [BUTTON_FINISH]],
        resize_keyboard=True,
    )
