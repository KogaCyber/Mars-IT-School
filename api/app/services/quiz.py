"""Test: savollarni tanlash va natijani hisoblash (Django versiyasidan ko'chirilgan)."""

import random
import secrets
from collections import Counter, defaultdict

from ..models.site import Option, Outcome, Question, Quiz, Submission


def sample_questions(quiz: Quiz) -> list[Question]:
    """Har urinishda `questions_per_attempt` ta tasodifiy savol, aralash tartibda."""
    questions = list(quiz.questions)
    limit = quiz.questions_per_attempt
    if not limit:
        return questions
    if len(questions) > limit:
        questions = random.sample(questions, limit)  # noqa: S311 — kriptografiya emas
    random.shuffle(questions)
    return questions


def _skill_percentages(by_question: dict[str, list[Option]], answers: dict) -> dict:
    earned: Counter[str] = Counter()
    maximum: Counter[str] = Counter()
    for question_id, option_id in answers.items():
        options = by_question.get(str(question_id))
        if not options:
            continue
        best: dict[str, int] = {}
        for option in options:
            if option.skill:
                best[option.skill] = max(best.get(option.skill, 0), option.weight)
        for skill, weight in best.items():
            maximum[skill] += weight
        chosen = next((o for o in options if str(o.id) == str(option_id)), None)
        if chosen and chosen.skill:
            earned[chosen.skill] += chosen.weight
    return {s: round(earned[s] * 100 / total) for s, total in maximum.items() if total}


def evaluate(quiz: Quiz, options: list[Option], outcomes: list[Outcome], answers: dict[str, str]) -> Submission:
    """`answers` — {"<question_id>": "<option_id>"}. Notanish id'lar e'tiborga olinmaydi.

    Ballar teng bo'lsa — birinchi tanlangan javobning yo'nalishi g'olib.
    """
    option_ids = [str(v) for v in answers.values() if v]
    by_id = {str(o.id): o for o in options}
    by_question: dict[str, list[Option]] = defaultdict(list)
    for o in options:
        by_question[str(o.question_id)].append(o)

    scores: Counter[str] = Counter()
    order: list[str] = []
    for option_id in option_ids:
        option = by_id.get(option_id)
        if not option or not option.outcome_id:
            continue
        key = str(option.outcome_id)
        scores[key] += option.weight
        if key not in order:
            order.append(key)

    outcome = None
    if scores:
        winner = max(scores, key=lambda k: (scores[k], -order.index(k)))
        outcome = next((o for o in outcomes if str(o.id) == winner), None)

    return Submission(
        public_token=secrets.token_urlsafe(32),
        quiz_id=quiz.id,
        outcome_id=outcome.id if outcome else None,
        answers=answers,
        scores=dict(scores),
        skills=_skill_percentages(by_question, answers),
    )


SKILL_LABELS: dict[str, dict[str, str]] = {
    "logic": {
        "ru": "Логическое мышление",
        "uz": "Mantiqiy tafakkur",
        "en": "Logical thinking",
    },
    "math": {
        "ru": "Математическое мышление",
        "uz": "Matematik tafakkur",
        "en": "Mathematical thinking",
    },
    "accuracy": {
        "ru": "Точность и порядок",
        "uz": "Aniqlik va tartib",
        "en": "Precision and order",
    },
    "patience": {
        "ru": "Терпение",
        "uz": "Sabr",
        "en": "Patience",
    },
    "creativity": {
        "ru": "Креативность",
        "uz": "Ijodkorlik",
        "en": "Creativity",
    },
    "visual": {
        "ru": "Визуальное восприятие",
        "uz": "Vizual idrok",
        "en": "Visual perception",
    },
    "communication": {
        "ru": "Коммуникабельность",
        "uz": "Muloqotchanlik",
        "en": "Communication",
    },
    "social": {
        "ru": "Социальная активность",
        "uz": "Ijtimoiy faollik",
        "en": "Social activity",
    },
}


def skill_label(code: str, lang: str) -> str:
    names = SKILL_LABELS.get(code)
    return (names.get(lang) or names["ru"]) if names else code
