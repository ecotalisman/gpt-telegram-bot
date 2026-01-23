from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass(frozen=True)
class QuizQuestion:
    question: str
    options: List[str]
    answer: str


def normalize_choice(text: str) -> Optional[str]:
    """Return 'A'/'B'/'C'/'D' if the user typed a choice, else None"""
    t = (text or "").strip().upper()
    if not t:
        return None
    t = t[0]
    return t if t in {"A", "B", "C", "D"} else None


def letters_for_options(n: int) -> List[str]:
    return ["A", "B", "C", "D"][:n]


def correct_letter(q: QuizQuestion) -> str:
    try:
        idx = q.options.index(q.answer)
        return letters_for_options(len(q.options))[idx]
    except ValueError:
        return "?"


def format_question_html(q: QuizQuestion, index: int, total: int) -> str:
    letters = letters_for_options(len(q.options))
    lines = [
        f"🧠 <b>Quiz</b> — Question <b>{index}/{total}</b>\n",
        f"<b>{q.question}</b>\n",
    ]
    for i, opt in enumerate(q.options):
        lines.append(f"<b>{letters[i]})</b> {opt}")
    lines.append("\nReply with: <b>A</b>, <b>B</b>, <b>C</b>" + (", <b>D</b>" if len(q.options) == 4 else ""))
    return "\n".join(lines)


def evaluate(q: QuizQuestion, user_choice_letter: str) -> Tuple[bool, str]:
    letters = letters_for_options(len(q.options))
    idx = letters.index(user_choice_letter)
    chosen = q.options[idx]
    is_correct = (chosen == q.answer)

    cor_letter = correct_letter(q)
    if is_correct:
        feedback = f"✅ Correct! (<b>{user_choice_letter}</b>)"
    else:
        feedback = (
            f"❌ Wrong. You chose <b>{user_choice_letter}</b>, "
            f"correct is <b>{cor_letter}</b>"
        )

    feedback += f"\n<b>Correct answer:</b> {cor_letter}) {q.answer}"
    return is_correct, feedback


def format_final_html(score: int, total: int, topic: str) -> str:
    return (
        f"🎉 <b>Quiz Complete!</b>\n"
        f"Topic: <b>{topic}</b>\n"
        f"Score: <b>{score}/{total}</b>"
    )
