"""Test savollarini tanlash va natijani hisoblash mantiqi."""

import random
from collections import Counter, defaultdict

from .models import Option, Outcome, Question, Quiz, Submission


def sample_questions(quiz: Quiz) -> list[Question]:
    """Bir urinish uchun savollarni tasodifiy tanlaydi.

    Savollar bazasi (masalan 30 ta savol) bitta testda to'liq ko'rsatilmaydi:
    har safar `quiz.questions_per_attempt` (standart — 20) ta savol tasodifiy
    olinadi va tartibi ham aralashtiriladi. Shu tufayli ikki kishi (yoki bitta
    kishi ikki marta) bir xil testni ko'rmaydi.

    `questions_per_attempt = 0` bo'lsa — barcha savollar, o'z tartibida.
    """
    questions = list(quiz.questions.prefetch_related("options"))
    limit = quiz.questions_per_attempt

    if not limit:
        return questions

    if len(questions) > limit:
        questions = random.sample(questions, limit)
    random.shuffle(questions)
    return questions


def _skill_percentages(options_by_question: dict[str, list[Option]], answers: dict) -> dict:
    """Har bir ko'nikma bo'yicha «necha foizga» belgi berilganini hisoblaydi.

    Har bir javob varianti bitta ko'nikmani ko'rsatadi. Berilgan savolda shu
    ko'nikma bo'yicha eng yuqori ball — «maksimum», tanlangan javob bergan ball
    — «to'plangan». Foiz shu ikkisining nisbati: ko'nikma taklif qilingan-u,
    tanlanmagan bo'lsa — 0%, doim tanlangan bo'lsa — 100%.
    """
    earned: Counter[str] = Counter()
    maximum: Counter[str] = Counter()

    for question_id, option_id in answers.items():
        options = options_by_question.get(str(question_id))
        if not options:
            continue

        best: dict[str, int] = {}
        for option in options:
            if option.skill:
                best[option.skill] = max(best.get(option.skill, 0), option.weight)
        for skill, weight in best.items():
            maximum[skill] += weight

        chosen = next((item for item in options if str(item.pk) == str(option_id)), None)
        if chosen and chosen.skill:
            earned[chosen.skill] += chosen.weight

    return {skill: round(earned[skill] * 100 / total) for skill, total in maximum.items() if total}


def evaluate(quiz: Quiz, answers: dict[str, str]) -> Submission:
    """Tanlangan variantlar bo'yicha eng ko'p ball to'plagan natijani aniqlaydi.

    `answers` — `{"<question_id>": "<option_id>"}` ko'rinishida. Noto'g'ri yoki
    boshqa testga tegishli identifikatorlar e'tiborga olinmaydi.

    Ballar teng bo'lsa (masalan 10:10), foydalanuvchi eng birinchi tanlagan
    javobning yo'nalishi g'olib bo'ladi — bu birinchi, eng «beg'araz» javob.
    """
    option_ids = [value for value in answers.values() if value]

    # Savolning barcha variantlari kerak: tanlangani — natija uchun, qolganlari —
    # ko'nikma foizining maksimumini hisoblash uchun.
    options = Option.objects.filter(question_id__in=list(answers), question__quiz=quiz)
    by_id = {str(option.pk): option for option in options if str(option.pk) in set(option_ids)}
    by_question: dict[str, list[Option]] = defaultdict(list)
    for option in options:
        by_question[str(option.question_id)].append(option)

    scores: Counter[str] = Counter()
    order: list[str] = []  # natijalar javob berilgan tartibda
    for option_id in option_ids:
        option = by_id.get(str(option_id))
        if not option or not option.outcome_id:
            continue
        outcome_id = str(option.outcome_id)
        scores[outcome_id] += option.weight
        if outcome_id not in order:
            order.append(outcome_id)

    outcome: Outcome | None = None
    if scores:
        outcome_id = max(scores, key=lambda key: (scores[key], -order.index(key)))
        outcome = Outcome.objects.filter(pk=outcome_id).first()

    return Submission(
        quiz=quiz,
        outcome=outcome,
        answers=answers,
        scores=dict(scores),
        skills=_skill_percentages(by_question, answers),
    )
