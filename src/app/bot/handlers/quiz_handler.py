from __future__ import annotations

import html

from telegram import Update
from telegram.ext import ContextTypes

from src.app.settings.config import settings
from src.app.bot.keyboards import (
    BUTTON_FINISH,
    BUTTON_ANOTHER_QUESTION,
    BUTTON_CHANGE_TOPIC,
    QUIZZ_TOPICS,
    quiz_topic_keyboard,
    quiz_answer_keyboard,
    quiz_action_keyboard,
    main_keyboard,
)
from src.app.bot.message_sender import send_html_message
from src.app.bot.resource_loader import load_prompt

from src.app.db.enums import SessionMode, MessageRole
from src.app.db.repository import GptThreadRepository
from src.app.services.openai_client import OpenAIClient

from src.app.bot.utils.openai_quiz import ask_quiz_with_retries
from src.app.bot.utils.quiz import (
    normalize_choice,
    letters_for_options,
    format_question_html,
    evaluate,
    format_final_html,
    QuizQuestion,
)

QUIZ_STATE = "quiz_state"
STATE_CHOOSE_TOPIC = "choose_topic"
STATE_AWAIT_ANSWER = "await_answer"
STATE_AWAIT_NEXT = "await_next"

KEY_TOPIC = "quiz_topic"
KEY_QUESTIONS = "quiz_questions"   # list[QuizQuestion]
KEY_INDEX = "quiz_index"           # next question index (0-based)
KEY_SCORE = "quiz_score"


def _reset_quiz_userdata(context: ContextTypes.DEFAULT_TYPE) -> None:
    for k in [QUIZ_STATE, KEY_TOPIC, KEY_QUESTIONS, KEY_INDEX, KEY_SCORE]:
        context.user_data.pop(k, None)


async def _show_choose_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[QUIZ_STATE] = STATE_CHOOSE_TOPIC
    await send_html_message(
        update,
        context,
        "🧠 <b>Quiz mode</b>\nChoose a topic:",
        reply_markup=quiz_topic_keyboard(),
    )


async def _show_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions: list[QuizQuestion] = context.user_data.get(KEY_QUESTIONS, [])
    idx: int = int(context.user_data.get(KEY_INDEX, 0))
    topic: str = context.user_data.get(KEY_TOPIC, "Unknown")

    if not questions:
        await send_html_message(update, context, "⚠️ No questions loaded. Choose a topic again.")
        await _show_choose_topic(update, context)
        return

    if idx >= len(questions):
        # finished
        score = int(context.user_data.get(KEY_SCORE, 0))
        total = len(questions)
        await send_html_message(
            update,
            context,
            format_final_html(score, total, topic),
            reply_markup=quiz_action_keyboard(),
        )
        context.user_data[QUIZ_STATE] = STATE_AWAIT_NEXT
        return

    q = questions[idx]
    total = len(questions)
    letters = letters_for_options(len(q.options))

    await send_html_message(
        update,
        context,
        format_question_html(q, idx + 1, total),
        reply_markup=quiz_answer_keyboard(letters),
    )
    context.user_data[QUIZ_STATE] = STATE_AWAIT_ANSWER


async def _generate_questions(update: Update, context: ContextTypes.DEFAULT_TYPE, topic: str) -> None:
    client: OpenAIClient = context.bot_data["openai_client"]
    repo: GptThreadRepository = context.bot_data["thread_repository"]

    tg_user_id = update.effective_user.id if update.effective_user else 0
    mode = SessionMode.QUIZ.value

    conversation_id, last_response_id = await repo.get_or_create_session(tg_user_id, mode)

    await send_html_message(update, context, f"⏳ Generating quiz for <b>{topic}</b>...")

    system_prompt = load_prompt("quiz")

    questions, new_response_id = await ask_quiz_with_retries(
        client=client,
        system_prompt=system_prompt,
        model=settings.openai_model,
        topic=topic,
        previous_response_id=last_response_id,
        max_attempts=2,
    )

    # store session continuation id
    await repo.set_last_response_id(tg_user_id, mode, new_response_id)

    # store locally in user_data
    context.user_data[KEY_TOPIC] = topic
    context.user_data[KEY_QUESTIONS] = questions
    context.user_data[KEY_INDEX] = 0
    context.user_data[KEY_SCORE] = 0

    # store to DB history
    await repo.add_message(conversation_id, MessageRole.USER.value, f"[QUIZ] Topic chosen: {topic}")
    await repo.add_message(conversation_id, MessageRole.ASSISTANT.value, f"[QUIZ] Generated {len(questions)} questions.")

    await _show_question(update, context)


async def handle_quiz_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str) -> None:
    text = (user_text or "").strip()

    if text == BUTTON_FINISH:
        _reset_quiz_userdata(context)
        context.user_data["mode"] = SessionMode.GPT.value
        await send_html_message(
            update,
            context,
            "✅ Quiz finished. Back to <b>GPT</b>.",
            reply_markup=main_keyboard(),
        )
        return

    state = context.user_data.get(QUIZ_STATE)

    # If user just entered quiz mode and state not set yet
    if state is None:
        await _show_choose_topic(update, context)
        return

    # ----- Choose topic -----
    if state == STATE_CHOOSE_TOPIC:
        if text in QUIZZ_TOPICS:
            try:
                await _generate_questions(update, context, text)
            except Exception as e:
                err = html.escape(f"{type(e).__name__}: {e}")
                await send_html_message(update, context, f"⚠️ Quiz generate error:\n<code>{err}</code>")
                await _show_choose_topic(update, context)
            return

        await send_html_message(update, context, "Choose a topic from the buttons 👇", reply_markup=quiz_topic_keyboard())
        return

    # ----- Await answer -----
    if state == STATE_AWAIT_ANSWER:
        choice = normalize_choice(text)
        if choice is None:
            await send_html_message(update, context, "Reply with <b>A</b>/<b>B</b>/<b>C</b>/<b>D</b> 👇")
            return

        questions: list[QuizQuestion] = context.user_data.get(KEY_QUESTIONS, [])
        idx: int = int(context.user_data.get(KEY_INDEX, 0))

        if idx >= len(questions):
            await _show_question(update, context)
            return

        q = questions[idx]
        is_correct, feedback = evaluate(q, choice)

        if is_correct:
            context.user_data[KEY_SCORE] = int(context.user_data.get(KEY_SCORE, 0)) + 1

        repo: GptThreadRepository = context.bot_data["thread_repository"]
        tg_user_id = update.effective_user.id if update.effective_user else 0
        conversation_id, _ = await repo.get_or_create_session(tg_user_id, SessionMode.QUIZ.value)
        await repo.add_message(conversation_id, MessageRole.USER.value, f"[QUIZ] Q{idx+1} answer: {choice}")
        await repo.add_message(conversation_id, MessageRole.ASSISTANT.value, f"[QUIZ] Feedback: {feedback}")

        # Move pointer to next question, but show action keyboard first
        context.user_data[KEY_INDEX] = idx + 1
        context.user_data[QUIZ_STATE] = STATE_AWAIT_NEXT

        await send_html_message(update, context, feedback, reply_markup=quiz_action_keyboard())
        return

    # ----- Await next action -----
    if state == STATE_AWAIT_NEXT:
        if text == BUTTON_CHANGE_TOPIC:
            _reset_quiz_userdata(context)
            await _show_choose_topic(update, context)
            return

        if text == BUTTON_ANOTHER_QUESTION:
            await _show_question(update, context)
            return

        # If user types a choice here, tell them to press "Another question"
        if normalize_choice(text) is not None:
            await send_html_message(update, context, "Press <b>Another question</b> to continue 👇", reply_markup=quiz_action_keyboard())
            return

        await send_html_message(update, context, "Use the buttons 👇", reply_markup=quiz_action_keyboard())
        return

    # Fallback
    await _show_choose_topic(update, context)
