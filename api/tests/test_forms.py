"""Formalar: ariza, vakansiyaga otklik, test."""

from sqlalchemy import select

from app.models import site as m


async def test_lead_is_saved_with_normalized_phone(client, db, course):
    r = await client.post(
        "/api/v1/leads/",
        json={
            "full_name": "  Malika   Karimova ",
            "phone": "+998 (90) 111-22-33",
            "course": "it-kids",
            "source": "course",
        },
    )
    assert r.status_code == 201, r.text
    lead = (await db.execute(select(m.Lead))).scalar_one()
    assert lead.full_name == "Malika Karimova"
    assert lead.phone == "+998901112233"
    assert lead.course_id == course.id
    assert lead.admin_note == ""


async def test_lead_survives_unknown_course_slug(client, db):
    """Kurs topilmasa ARIZA YO'QOLMAYDI — mijozning telefoni saqlanadi."""
    r = await client.post("/api/v1/leads/", json={"full_name": "Anvar", "phone": "901112244", "course": "yoq-kurs"})
    assert r.status_code == 201
    lead = (await db.execute(select(m.Lead))).scalar_one()
    assert lead.course_id is None
    assert "yoq-kurs" in lead.admin_note


async def test_lead_honeypot_rejected(client, db):
    r = await client.post("/api/v1/leads/", json={"full_name": "Bot", "phone": "901112255", "website": "spam"})
    assert r.status_code == 400
    assert (await db.execute(select(m.Lead))).scalar_one_or_none() is None


async def test_lead_rejects_bad_phone_and_short_name(client):
    assert (await client.post("/api/v1/leads/", json={"full_name": "A", "phone": "901112266"})).status_code == 400
    assert (await client.post("/api/v1/leads/", json={"full_name": "Ali", "phone": "+7 999"})).status_code == 400


async def test_lead_message_follows_language(client):
    ru = await client.post("/api/v1/leads/", json={"full_name": "Ali", "phone": "901112277"}, params={"lang": "ru"})
    uz = await client.post("/api/v1/leads/", json={"full_name": "Ali", "phone": "901112288"}, params={"lang": "uz"})
    assert "заявка" in ru.json()["detail"].lower()
    assert "ariza" in uz.json()["detail"].lower()


# --- vakansiya -------------------------------------------------------------


async def _vacancy(db):
    v = m.Vacancy(slug="python-teacher", title_ru="Python o'qituvchisi", description_ru="x", requirements_ru="y")
    db.add(v)
    await db.commit()
    return v


async def test_vacancy_application_accepts_real_pdf(client, db):
    await _vacancy(db)
    r = await client.post(
        "/api/v1/vacancy-applications/",
        data={"vacancy": "python-teacher", "full_name": "Ali Valiyev", "phone": "901112299"},
        files={"resume": ("cv.pdf", b"%PDF-1.4 fake body", "application/pdf")},
    )
    assert r.status_code == 201, r.text
    app_ = (await db.execute(select(m.VacancyApplication))).scalar_one()
    assert app_.resume.startswith("resumes/") and app_.resume.endswith(".pdf")
    assert "cv" not in app_.resume  # nomzod nomi diskda yo'q


async def test_vacancy_application_rejects_fake_pdf(client, db):
    """`.pdf` deb nomlangan HTML — mazmun tekshiruvi."""
    await _vacancy(db)
    r = await client.post(
        "/api/v1/vacancy-applications/",
        data={"vacancy": "python-teacher", "full_name": "Ali Valiyev", "phone": "901112299"},
        files={"resume": ("cv.pdf", b"<html><script>alert(1)</script>", "application/pdf")},
    )
    assert r.status_code == 400
    assert (await db.execute(select(m.VacancyApplication))).scalar_one_or_none() is None


async def test_vacancy_application_rejects_exe(client, db):
    await _vacancy(db)
    r = await client.post(
        "/api/v1/vacancy-applications/",
        data={"vacancy": "python-teacher", "full_name": "Ali Valiyev", "phone": "901112299"},
        files={"resume": ("cv.exe", b"MZ....", "application/octet-stream")},
    )
    assert r.status_code == 400


async def test_closed_vacancy_is_hidden_and_rejects(client, db):
    v = await _vacancy(db)
    v.is_open = False
    await db.commit()
    assert (await client.get("/api/v1/vacancies/")).json() == []
    r = await client.post(
        "/api/v1/vacancy-applications/",
        data={"vacancy": "python-teacher", "full_name": "Ali Valiyev", "phone": "901112299"},
    )
    assert r.status_code == 422


# --- test (quiz) -----------------------------------------------------------


async def _quiz(db, course):
    quiz = m.Quiz(slug="proforientatsiya", title_ru="Тест", questions_per_attempt=0)
    db.add(quiz)
    await db.flush()
    prog = m.Outcome(quiz_id=quiz.id, code="programming", title_ru="Программирование")
    design = m.Outcome(quiz_id=quiz.id, code="design", title_ru="Дизайн")
    db.add_all([prog, design])
    await db.flush()
    db.add(m.OutcomeCourse(outcome_id=prog.id, course_id=course.id))
    q1 = m.Question(quiz_id=quiz.id, text_ru="Q1", order=1)
    q2 = m.Question(quiz_id=quiz.id, text_ru="Q2", order=2)
    db.add_all([q1, q2])
    await db.flush()
    db.add_all(
        [
            m.Option(question_id=q1.id, outcome_id=prog.id, text_ru="код", skill="logic", weight=2),
            m.Option(question_id=q1.id, outcome_id=design.id, text_ru="рисунок", skill="creativity", weight=1),
            m.Option(question_id=q2.id, outcome_id=prog.id, text_ru="логика", skill="logic", weight=1),
            m.Option(question_id=q2.id, outcome_id=design.id, text_ru="цвет", skill="creativity", weight=1),
        ]
    )
    await db.commit()
    return quiz, q1, q2, prog


async def test_quiz_flow(client, db, course):
    quiz, q1, q2, prog = await _quiz(db, course)

    data = (await client.get("/api/v1/quizzes/proforientatsiya/")).json()
    assert data["slug"] == "proforientatsiya" and len(data["questions"]) == 2
    assert all(len(q["options"]) == 2 for q in data["questions"])
    assert "id" in data["questions"][0]["options"][0]

    options = {q["id"]: [o["id"] for o in q["options"]] for q in data["questions"]}
    # q1: birinchi ("код" -> programming, weight 2), q2: "логика" -> programming
    q1_opts = (await db.execute(select(m.Option).where(m.Option.question_id == q1.id))).scalars().all()
    q2_opts = (await db.execute(select(m.Option).where(m.Option.question_id == q2.id))).scalars().all()
    kod = next(o for o in q1_opts if o.text_ru == "код")
    logika = next(o for o in q2_opts if o.text_ru == "логика")
    assert kod.id in options[q1.id] and logika.id in options[q2.id]

    r = await client.post(
        "/api/v1/quizzes/proforientatsiya/submit/",
        json={"answers": {str(q1.id): str(kod.id), str(q2.id): str(logika.id)}, "full_name": "Test", "phone": ""},
    )
    assert r.status_code == 201, r.text
    result = r.json()
    assert result["outcome"]["code"] == "programming"
    assert result["outcome"]["courses"][0]["slug"] == "it-kids"
    assert sum(x["percent"] for x in result["matches"]) == 100
    assert result["skills"][0]["code"] == "logic" and result["skills"][0]["percent"] == 100
    token = result["token"]
    assert len(token) >= 40 and "id" not in result  # havolada faqat token

    again = await client.get(f"/api/v1/quiz-results/{token}/")
    assert again.status_code == 200 and again.json()["outcome"]["code"] == "programming"
    assert again.headers["cache-control"] == "no-store, private"
    assert (await client.get("/api/v1/quiz-results/nope/")).status_code == 404


async def test_quiz_submit_ignores_garbage_keys(client, db, course):
    quiz, q1, q2, prog = await _quiz(db, course)
    r = await client.post("/api/v1/quizzes/proforientatsiya/submit/", json={"answers": {"abc": "def", "-1": "x"}})
    assert r.status_code == 400
    kod = (await db.execute(select(m.Option).where(m.Option.text_ru == "код"))).scalar_one()
    r = await client.post(
        "/api/v1/quizzes/proforientatsiya/submit/", json={"answers": {"abc": "def", str(q1.id): str(kod.id)}}
    )
    assert r.status_code == 201
