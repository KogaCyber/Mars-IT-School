"""Saytni tekshirish uchun namunaviy ma'lumot yaratadi.

Ishlatish:  python manage.py seed_demo
Faqat ishlab chiqish muhitida ishlatiladi.

Barcha matnlar uch tilda (`T(ru, uz, en)`) yoziladi — sayt uz/ru/en da
ishlagani uchun namunaviy ma'lumot ham uchala tilni to'ldiradi. Bo'sh
tarjima qolsa, API asosiy tilga (ru) qaytadi va sayt bir tilli bo'lib
ko'rinadi.
"""

from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.branches.models import Branch
from apps.core.models import (
    FAQ,
    Advantage,
    ChildSkill,
    Founder,
    FutureBenefit,
    ParentReview,
    ProjectDefenceStep,
    SchoolFeature,
    SiteSettings,
    SpaceFeature,
    Statistic,
)
from apps.courses.models import Course, CourseStage, Direction
from apps.news.models import News, NewsCategory, NewsImage
from apps.quiz.seeding import ensure_quiz
from apps.teachers.models import Skill as TechSkill
from apps.teachers.models import Teacher
from apps.vacancies.models import Vacancy

# Namunaviy rasmlar shu papkada saqlanadi (git bilan birga keladi).
IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "images"


class T(tuple):
    """Uch tilli matn: `T("ru", "uz", "en")`.

    `fields("title")` chaqirilganda `{"title_ru": …, "title_uz": …, "title_en": …}`
    lug'atini beradi — uni to'g'ridan-to'g'ri `defaults` ichiga yoyish mumkin.
    """

    __slots__ = ()

    def __new__(cls, ru: str, uz: str, en: str):
        return super().__new__(cls, (ru, uz, en))

    def fields(self, name: str) -> dict[str, str]:
        return {f"{name}_ru": self[0], f"{name}_uz": self[1], f"{name}_en": self[2]}

    @property
    def ru(self) -> str:
        return self[0]


def attach_image(instance, field_name: str, file_name: str) -> None:
    """Fixtures papkasidagi rasmni model maydoniga biriktiradi (bir marta)."""
    field = getattr(instance, field_name)
    source = IMAGES_DIR / file_name
    if field or not source.exists():
        return
    with source.open("rb") as fh:
        field.save(file_name, File(fh), save=True)


ADVANTAGES = [
    (
        "01",
        T(
            "Современная программа",
            "Zamonaviy dastur",
            "A modern curriculum",
        ),
        T(
            "Изучаем актуальные технологии, которые используются в реальной разработке.",
            "Haqiqiy ishlab chiqishda qo‘llanadigan dolzarb texnologiyalarni o‘rganamiz.",
            "We teach the current technologies used in real-world development.",
        ),
    ),
    (
        "02",
        T(
            "Опытные преподаватели",
            "Tajribali o‘qituvchilar",
            "Experienced teachers",
        ),
        T(
            "Практикующие специалисты, которые объясняют сложные темы простым языком.",
            "Murakkab mavzularni sodda tilda tushuntiradigan amaliyotchi mutaxassislar.",
            "Working professionals who explain complex topics in simple language.",
        ),
    ),
    (
        "03",
        T(
            "Собственная платформа SPACE",
            "O‘zimizning SPACE platformamiz",
            "Our own SPACE platform",
        ),
        T(
            "Всё обучение, домашние задания и успеваемость доступны в одном месте.",
            "Barcha darslar, uy vazifalari va o‘zlashtirish bir joyda.",
            "All lessons, homework and progress in one place.",
        ),
    ),
    (
        "04",
        T(
            "Небольшие группы",
            "Kichik guruhlar",
            "Small groups",
        ),
        T(
            "Каждому ученику уделяется достаточно внимания во время занятий.",
            "Dars davomida har bir o‘quvchiga yetarli e’tibor qaratiladi.",
            "Every student gets enough attention during class.",
        ),
    ),
    (
        "05",
        T(
            "Практика вместо теории",
            "Nazariya emas — amaliyot",
            "Practice instead of theory",
        ),
        T(
            "Ученики регулярно создают собственные проекты, а не только слушают лекции.",
            "O‘quvchilar faqat ma’ruza tinglamaydi — muntazam o‘z loyihalarini yaratadi.",
            "Students regularly build their own projects, not just listen to lectures.",
        ),
    ),
    (
        "06",
        T(
            "Мероприятия и сообщество",
            "Tadbirlar va hamjamiyat",
            "Events and community",
        ),
        T(
            "Каждое воскресенье события, где дети знакомятся и общаются.",
            "Har yakshanba bolalar tanishadigan va muloqot qiladigan tadbirlar.",
            "Every Sunday there are events where children meet and socialise.",
        ),
    ),
]

SPACE_FEATURES = [
    (
        T("Домашние задания", "Uy vazifalari", "Homework"),
        T(
            "Все задания и дедлайны в одном списке.",
            "Barcha vazifalar va muddatlar bitta ro‘yxatda.",
            "All assignments and deadlines in one list.",
        ),
    ),
    (
        T("Записи занятий", "Dars yozuvlari", "Lesson recordings"),
        T(
            "Пропущенный урок можно посмотреть в записи.",
            "O‘tkazib yuborilgan darsni yozuvdan ko‘rish mumkin.",
            "A missed lesson can be watched as a recording.",
        ),
    ),
    (
        T("Успеваемость", "O‘zlashtirish", "Progress"),
        T(
            "Прозрачная статистика прогресса ученика.",
            "O‘quvchi taraqqiyotining shaffof statistikasi.",
            "Transparent statistics on the student's progress.",
        ),
    ),
    (
        T("Баллы и награды", "Ballar va mukofotlar", "Points and rewards"),
        T(
            "Игровая мотивация: баллы за задания и активность.",
            "O‘yin shaklidagi rag‘bat: vazifa va faollik uchun ballar.",
            "Game-style motivation: points for assignments and activity.",
        ),
    ),
    (
        T("Общение", "Muloqot", "Chat"),
        T(
            "Чат с преподавателем и одногруппниками.",
            "O‘qituvchi va guruhdoshlar bilan chat.",
            "Chat with the teacher and classmates.",
        ),
    ),
    (
        T("MARS Shop", "MARS Shop", "MARS Shop"),
        T(
            "Магазин, где баллы обмениваются на призы.",
            "Ballarni sovg‘alarga almashtiradigan do‘kon.",
            "A shop where points are exchanged for prizes.",
        ),
    ),
]

# «Почему это важно для будущего» — «О нас» sahifasi
FUTURE_BENEFITS = [
    (
        T(
            "Технологии вокруг нас",
            "Atrofimizdagi texnologiyalar",
            "Technology all around us",
        ),
        T(
            "Понимание технологий, которые окружают ребёнка каждый день",
            "Bolani har kuni o‘rab turgan texnologiyalarni tushunish",
            "Understanding the technology that surrounds a child every day",
        ),
    ),
    (
        T(
            "Самостоятельное мышление",
            "Mustaqil fikrlash",
            "Independent thinking",
        ),
        T(
            "Навык самостоятельного поиска решений и работы с информацией",
            "Mustaqil yechim izlash va axborot bilan ishlash ko‘nikmasi",
            "The skill of finding solutions independently and working with information",
        ),
    ),
    (
        T(
            "Востребованная профессия",
            "Talab yuqori kasb",
            "An in-demand profession",
        ),
        T(
            "Ранний старт в профессии с высоким спросом на рынке труда",
            "Mehnat bozorida talab yuqori bo‘lgan kasbda erta start",
            "An early start in a profession with high demand on the job market",
        ),
    ),
    (
        T(
            "Уверенность через практику",
            "Amaliyot orqali ishonch",
            "Confidence through practice",
        ),
        T(
            "Уверенность в себе через реальные завершённые проекты",
            "Yakuniga yetkazilgan haqiqiy loyihalar orqali o‘ziga ishonch",
            "Self-confidence through real, completed projects",
        ),
    ),
]

# «Какие навыки развивает ребёнок»
CHILD_SKILLS = [
    (
        T("Логическое мышление", "Mantiqiy tafakkur", "Logical thinking"),
        T(
            "Ребёнок учится раскладывать задачу на шаги и находить закономерности.",
            "Bola masalani bosqichlarga ajratishni va qonuniyatlarni topishni o‘rganadi.",
            "The child learns to break a task into steps and spot patterns.",
        ),
        "brain",
    ),
    (
        T("Системность", "Tizimlilik", "Systematic approach"),
        T(
            "Появляется привычка доводить проект от идеи до работающего результата.",
            "Loyihani g‘oyadan ishlaydigan natijagacha yetkazish odati shakllanadi.",
            "A habit forms of taking a project from idea to working result.",
        ),
        "layers",
    ),
    (
        T("Анализ информации", "Axborot tahlili", "Information analysis"),
        T(
            "Учится проверять источники, читать документацию и искать решения.",
            "Manbalarni tekshirish, hujjatlarni o‘qish va yechim izlashni o‘rganadi.",
            "Learns to check sources, read documentation and look for solutions.",
        ),
        "target",
    ),
    (
        T("Проектное мышление", "Loyihaviy tafakkur", "Project thinking"),
        T(
            "Планирует работу, распределяет роли в команде и защищает результат.",
            "Ishni rejalashtiradi, jamoada rollarni taqsimlaydi va natijani himoya qiladi.",
            "Plans the work, shares out roles in the team and defends the result.",
        ),
        "cubes",
    ),
]

# «День, когда ребёнок защищает свой проект»
PROJECT_DEFENCE_STEPS = [
    (
        T("1 раз", "1 marta", "Once"),
        T("в 3 месяца", "3 oyda", "every 3 months"),
        "calendar",
    ),
    (
        T("34", "34", "34"),
        T(
            "проекта на последнем Demo Day",
            "so‘nggi Demo Day’da loyiha",
            "projects at the last Demo Day",
        ),
        "checklist",
    ),
    (
        T("5 мин", "5 daq", "5 min"),
        T(
            "на защиту проекта",
            "loyiha himoyasiga",
            "to present a project",
        ),
        "clock",
    ),
]

# «Кто стоит за школой» — asoschilar
FOUNDERS = [
    (
        "Отабек Мирзаев",
        T("CEO", "CEO", "CEO"),
        T(
            "15 лет в IT и образовании, запустил 7 филиалов школы в Ташкенте.",
            "IT va ta’limda 15 yil, Toshkentda maktabning 7 ta filialini ochgan.",
            "15 years in IT and education; opened 7 branches of the school in Tashkent.",
        ),
        "teacher-1.webp",
    ),
    (
        "Санжар Рахимов",
        T("CTO", "CTO", "CTO"),
        T(
            "Отвечает за платформу SPACE и техническую часть обучения.",
            "SPACE platformasi va o‘qitishning texnik qismi uchun javob beradi.",
            "Responsible for the SPACE platform and the technical side of teaching.",
        ),
        "teacher-2.webp",
    ),
    (
        "Камила Юсупова",
        T("Академический директор", "Akademik direktor", "Academic director"),
        T(
            "Формирует программы курсов и следит за качеством преподавания.",
            "Kurs dasturlarini shakllantiradi va o‘qitish sifatini nazorat qiladi.",
            "Shapes the course programmes and oversees teaching quality.",
        ),
        "teacher-3.webp",
    ),
]

# «MARS IT — это не просто курсы» ro'yxati
SCHOOL_FEATURES = [
    T(
        "Практические занятия вместо сухой теории",
        "Quruq nazariya emas — amaliy mashg‘ulotlar",
        "Hands-on classes instead of dry theory",
    ),
    T(
        "Современные лаборатории и оборудование",
        "Zamonaviy laboratoriya va jihozlar",
        "Modern labs and equipment",
    ),
    T(
        "Международная сертификация по итогам обучения",
        "O‘qish yakunida xalqaro sertifikat",
        "International certification on completion",
    ),
    T(
        "Постоянная поддержка куратора и преподавателя",
        "Kurator va o‘qituvchining doimiy yordami",
        "Ongoing support from a curator and teacher",
    ),
]

FAQS = [
    (
        T(
            "С какого возраста обучение?",
            "Necha yoshdan o‘qitasiz?",
            "From what age do you teach?",
        ),
        T(
            "Мы принимаем детей с 7 лет — программа подбирается по возрасту.",
            "Biz bolalarni 7 yoshdan qabul qilamiz — dastur yoshga qarab tanlanadi.",
            "We accept children from age 7 — the programme is matched to their age.",
        ),
    ),
    (
        T(
            "Нужен ли свой ноутбук?",
            "O‘z noutbuki kerakmi?",
            "Does my child need their own laptop?",
        ),
        T(
            "На занятиях в филиале техника предоставляется школой.",
            "Filialdagi darslarda texnikani maktab taqdim etadi.",
            "For classes at the branch, the school provides the equipment.",
        ),
    ),
    (
        T(
            "Что будет, если пропустить занятие?",
            "Darsni o‘tkazib yuborsa nima bo‘ladi?",
            "What happens if a lesson is missed?",
        ),
        T(
            "Запись урока доступна в платформе SPACE.",
            "Darsning yozuvi SPACE platformasida mavjud.",
            "The lesson recording is available on the SPACE platform.",
        ),
    ),
]

STATISTICS = [
    ("5 000+", T("выпускников", "bitiruvchi", "graduates")),
    ("1 200+", T("действующих учеников", "hozirgi o‘quvchi", "current students")),
    ("7", T("филиалов в Ташкенте", "Toshkentdagi filial", "branches in Tashkent")),
    ("40+", T("преподавателей", "o‘qituvchi", "teachers")),
]

REVIEWS = [
    (
        "Нодира Алимова",
        T("мама Алишера", "Alisherning onasi", "Alisher's mother"),
        T(
            "Сын ходит с удовольствием и уже сделал свой первый сайт.",
            "O‘g‘lim zavq bilan qatnaydi va allaqachon birinchi saytini yasadi.",
            "My son enjoys going and has already built his first website.",
        ),
        "review-1.webp",
    ),
    (
        "Дмитрий Ким",
        T("папа Софии", "Sofiyaning otasi", "Sofia's father"),
        T(
            "Дочь начала уверенно программировать уже через три месяца.",
            "Qizim uch oydan keyin ishonchli dasturlashni boshladi.",
            "My daughter was coding confidently after just three months.",
        ),
        "review-2.webp",
    ),
    (
        "Малика Юсупова",
        T("мама Тимура", "Timurning onasi", "Timur's mother"),
        T(
            "Нравится, что всё видно в приложении: задания, оценки, общение.",
            "Ilovada hammasi ko‘rinib turgani yoqadi: vazifalar, baholar, muloqot.",
            "I like that everything is visible in the app: assignments, grades, chat.",
        ),
        "review-3.webp",
    ),
]

WORK_HOURS = T(
    "Ежедневно с 09:00 до 20:00",
    "Har kuni 09:00 dan 20:00 gacha",
    "Daily from 09:00 to 20:00",
)


class Command(BaseCommand):
    help = "Namunaviy (demo) ma'lumotlarni yaratadi."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--force", action="store_true", help="Productionda ham ishlatish")

    def handle(self, *args, **options) -> None:
        if not settings.DEBUG and not options["force"]:
            raise CommandError(
                "Bu buyruq faqat DEBUG=True holatida ishlaydi (--force bilan majburlash mumkin)."
            )

        self._site_settings()
        self._advantages()
        self._future_benefits()
        self._child_skills()
        self._school_features()
        self._founders()
        self._project_defence()
        self._space_features()
        self._faqs()
        self._statistics()
        courses = self._courses()
        self._news()
        self._branches()
        self._vacancies()
        self._quiz(courses)
        self._reviews()

        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar tayyor."))

    def _site_settings(self) -> None:
        settings_obj = SiteSettings.load()
        settings_obj.phone = "+998 78 777 77 57"
        settings_obj.email = "info@marsit.uz"
        settings_obj.telegram_url = "https://t.me/marsitschool"
        settings_obj.instagram_url = "https://instagram.com/marsitschool"
        settings_obj.youtube_url = "https://youtube.com/@marsitschool"
        settings_obj.promo_video_url = "https://youtu.be/"
        for field, value in WORK_HOURS.fields("work_hours").items():
            setattr(settings_obj, field, value)
        settings_obj.save()
        attach_image(settings_obj, "promo_cover", "news-demoday.webp")

    def _advantages(self) -> None:
        for order, (number, title, description) in enumerate(ADVANTAGES, 1):
            advantage, _ = Advantage.objects.get_or_create(
                number=number,
                defaults={
                    **title.fields("title"),
                    **description.fields("description"),
                    "order": order,
                },
            )
            self._fill_translations(advantage, title=title, description=description)
            attach_image(advantage, "image", f"advantage-{number}.webp")

    def _future_benefits(self) -> None:
        for order, (title, description) in enumerate(FUTURE_BENEFITS, 1):
            benefit, _ = FutureBenefit.objects.get_or_create(
                title_ru=title.ru,
                defaults={
                    **title.fields("title"),
                    **description.fields("description"),
                    "order": order,
                },
            )
            self._fill_translations(benefit, title=title, description=description)

    def _child_skills(self) -> None:
        for order, (title, description, icon) in enumerate(CHILD_SKILLS, 1):
            skill, _ = ChildSkill.objects.get_or_create(
                title_ru=title.ru,
                defaults={
                    **title.fields("title"),
                    **description.fields("description"),
                    "icon_name": icon,
                    "order": order,
                },
            )
            self._fill_translations(skill, title=title, description=description)

    def _school_features(self) -> None:
        for order, title in enumerate(SCHOOL_FEATURES, 1):
            feature, _ = SchoolFeature.objects.get_or_create(
                title_ru=title.ru, defaults={**title.fields("title"), "order": order}
            )
            self._fill_translations(feature, title=title)

    def _founders(self) -> None:
        for order, (name, position, bio, image) in enumerate(FOUNDERS, 1):
            founder, _ = Founder.objects.get_or_create(
                full_name=name,
                defaults={
                    **position.fields("position"),
                    **bio.fields("bio"),
                    "order": order,
                },
            )
            self._fill_translations(founder, position=position, bio=bio)
            attach_image(founder, "photo", image)

    def _project_defence(self) -> None:
        for order, (label, caption, icon) in enumerate(PROJECT_DEFENCE_STEPS, 1):
            step, _ = ProjectDefenceStep.objects.get_or_create(
                label_ru=label.ru,
                defaults={
                    **label.fields("label"),
                    **caption.fields("title"),
                    "icon_name": icon,
                    "order": order,
                },
            )
            self._fill_translations(step, label=label, title=caption)

    def _space_features(self) -> None:
        screenshots = {
            "Домашние задания": "space-homework.webp",
            "Записи занятий": "space-lessons.webp",
            "Успеваемость": "space-progress.webp",
        }
        for order, (title, description) in enumerate(SPACE_FEATURES, 1):
            feature, _ = SpaceFeature.objects.get_or_create(
                title_ru=title.ru,
                defaults={
                    **title.fields("title"),
                    **description.fields("description"),
                    "order": order,
                },
            )
            self._fill_translations(feature, title=title, description=description)
            if title.ru in screenshots:
                attach_image(feature, "screenshot", screenshots[title.ru])

    def _faqs(self) -> None:
        for order, (question, answer) in enumerate(FAQS, 1):
            faq, _ = FAQ.objects.get_or_create(
                question_ru=question.ru,
                defaults={
                    **question.fields("question"),
                    **answer.fields("answer"),
                    "order": order,
                },
            )
            self._fill_translations(faq, question=question, answer=answer)

    def _statistics(self) -> None:
        for order, (value, label) in enumerate(STATISTICS, 1):
            statistic, _ = Statistic.objects.get_or_create(
                label_ru=label.ru,
                defaults={**label.fields("label"), "value": value, "order": order},
            )
            self._fill_translations(statistic, label=label)

    @staticmethod
    def _fill_translations(instance, **texts: T) -> None:
        """Mavjud yozuvdagi bo'sh tarjimalarni to'ldiradi.

        Buyruq idempotent: RU matn admin panelda o'zgartirilgan bo'lsa ham
        tegilmaydi, faqat bo'sh `_uz` / `_en` maydonlari to'ldiriladi —
        shunda eski bazada ham sayt uchala tilda ishlaydi.
        """
        updated = []
        for name, text in texts.items():
            for field, value in text.fields(name).items():
                if field.endswith("_ru"):
                    continue
                if not getattr(instance, field, "") and value:
                    setattr(instance, field, value)
                    updated.append(field)
        if updated:
            instance.save(update_fields=updated)

    def _teachers(self) -> list[Teacher]:
        skills = {}
        skill_icons = {
            "HTML": "skill-html.webp",
            "CSS": "skill-css.webp",
            "JavaScript": "skill-js.webp",
            "React": "skill-react.webp",
        }
        for order, name in enumerate(["HTML", "CSS", "JavaScript", "React", "Python", "Figma"], 1):
            skill, _ = TechSkill.objects.get_or_create(name=name, defaults={"order": order})
            if name in skill_icons:
                attach_image(skill, "icon", skill_icons[name])
            skills[name] = skill

        people = [
            {
                "name": "Дилшод Каримов",
                "badge": "Back-End",
                "position": T(
                    "Backend-разработчик",
                    "Backend-dasturchi",
                    "Backend developer",
                ),
                "years": 8,
                "students": 120,
                "bio": T(
                    "8 лет занимается разработкой серверных приложений на Python и Django, "
                    "проектирует API и надёжные backend-решения для коммерческих проектов.",
                    "8 yildan beri Python va Django’da server ilovalarini ishlab chiqadi, "
                    "tijorat loyihalari uchun API va ishonchli backend yechimlarini loyihalaydi.",
                    "Has spent 8 years building server applications in Python and Django, "
                    "designing APIs and reliable backend solutions for commercial projects.",
                ),
                "skills": ["Python", "JavaScript", "React"],
            },
            {
                "name": "Малика Каримова",
                "badge": "Robotics",
                "position": T(
                    "Преподаватель робототехники",
                    "Robototexnika o‘qituvchisi",
                    "Robotics teacher",
                ),
                "years": 5,
                "students": 90,
                "bio": T(
                    "5 лет помогает детям осваивать основы робототехники и Scratch, "
                    "переводя теорию в практику через реальные проекты.",
                    "5 yildan beri bolalarga robototexnika va Scratch asoslarini o‘rgatadi, "
                    "nazariyani haqiqiy loyihalar orqali amaliyotga aylantiradi.",
                    "Has spent 5 years helping children master the basics of robotics and "
                    "Scratch, turning theory into practice through real projects.",
                ),
                "skills": ["HTML", "CSS", "Figma"],
            },
            {
                "name": "Данила Карпов",
                "badge": "Front-End",
                "position": T(
                    "Frontend-разработчик",
                    "Frontend-dasturchi",
                    "Frontend developer",
                ),
                "years": 7,
                "students": 110,
                "bio": T(
                    "Создаёт интерфейсы на React и учит студентов писать чистый код.",
                    "React’da interfeyslar yaratadi va o‘quvchilarga toza kod yozishni o‘rgatadi.",
                    "Builds interfaces in React and teaches students to write clean code.",
                ),
                "skills": ["HTML", "CSS", "JavaScript", "React"],
            },
        ]

        teachers = []
        for order, person in enumerate(people, 1):
            teacher, created = Teacher.objects.get_or_create(
                full_name=person["name"],
                defaults={
                    "badge": person["badge"],
                    **person["position"].fields("position"),
                    **person["bio"].fields("bio"),
                    "experience_years": person["years"],
                    "students_count": person["students"],
                    "order": order,
                },
            )
            self._fill_translations(teacher, position=person["position"], bio=person["bio"])
            if created:
                teacher.skills.set([skills[name] for name in person["skills"]])
            attach_image(teacher, "photo", f"teacher-{order}.webp")
            teachers.append(teacher)
        return teachers

    def _courses(self) -> list[Course]:
        teacher = self._teachers()[0]

        items = [
            {
                "title": T("IT Kids", "IT Kids", "IT Kids"),
                "subtitle": T(
                    "Первое знакомство с технологиями через игру",
                    "O‘yin orqali texnologiyalar bilan ilk tanishuv",
                    "A first encounter with technology through play",
                ),
                "description": T(
                    "Курс «IT Kids» рассчитан на детей 7–10 лет.",
                    "«IT Kids» kursi 7–10 yoshli bolalar uchun mo‘ljallangan.",
                    "The IT Kids course is designed for children aged 7–10.",
                ),
                "age_from": 7,
                "age_to": 10,
            },
            {
                "title": T("Программирование", "Dasturlash", "Programming"),
                "subtitle": T(
                    "От основ до собственных проектов на Python и JavaScript",
                    "Asoslardan Python va JavaScript’dagi o‘z loyihalaringizgacha",
                    "From the basics to your own projects in Python and JavaScript",
                ),
                "description": T(
                    "Курс «Программирование» рассчитан на детей 11–17 лет.",
                    "«Dasturlash» kursi 11–17 yoshli bolalar uchun mo‘ljallangan.",
                    "The Programming course is designed for children aged 11–17.",
                ),
                "age_from": 11,
                "age_to": 17,
            },
        ]

        stages = [
            T("Знакомство", "Tanishuv", "Introduction"),
            T("Основы", "Asoslar", "Fundamentals"),
            T("Практика", "Amaliyot", "Practice"),
            T("Итоговый проект", "Yakuniy loyiha", "Final project"),
        ]

        courses = []
        for order, item in enumerate(items, 1):
            title = item["title"]
            direction, _ = Direction.objects.get_or_create(
                title_ru=title.ru, defaults={**title.fields("title"), "order": order}
            )
            self._fill_translations(direction, title=title)

            course, created = Course.objects.get_or_create(
                title_ru=title.ru,
                defaults={
                    "direction": direction,
                    **title.fields("title"),
                    **item["subtitle"].fields("subtitle"),
                    **item["description"].fields("description"),
                    "age_from": item["age_from"],
                    "age_to": item["age_to"],
                    "price": 800000,
                    "is_featured": True,
                    "order": order,
                },
            )
            self._fill_translations(
                course,
                title=title,
                subtitle=item["subtitle"],
                description=item["description"],
            )
            if created:
                course.teachers.add(teacher)
                for index, stage in enumerate(stages, 1):
                    CourseStage.objects.create(
                        course=course,
                        number=f"{index:02d}",
                        **stage.fields("title"),
                        duration_months=2,
                        order=index,
                    )
            else:
                for stage_obj, stage in zip(course.stages.order_by("order"), stages, strict=False):
                    self._fill_translations(stage_obj, title=stage)
            courses.append(course)
        return courses

    def _news(self) -> None:
        # Ilgari bitta umumiy turkum yaratilardi — endi ikkitaga bo'lingan.
        NewsCategory.objects.filter(title_ru="Новости и мероприятия", news__isnull=True).delete()

        news_title = T("Новости", "Yangiliklar", "News")
        events_title = T("Мероприятия", "Tadbirlar", "Events")

        news_category, _ = NewsCategory.objects.get_or_create(
            title_ru=news_title.ru, defaults=news_title.fields("title")
        )
        self._fill_translations(news_category, title=news_title)

        events_category, _ = NewsCategory.objects.get_or_create(
            title_ru=events_title.ru, defaults=events_title.fields("title")
        )
        self._fill_translations(events_category, title=events_title)

        # Har bir yangilikka namunaviy fotoreportaj (galereya) biriktiriladi.
        gallery_pool = [
            "advantage-01.webp",
            "advantage-02.webp",
            "advantage-03.webp",
            "advantage-04.webp",
            "advantage-05.webp",
            "advantage-06.webp",
        ]
        photo_caption = T("фото", "surat", "photo")

        items = [
            {
                "title": T(
                    "Прошёл футбольный турнир между филиалами",
                    "Filiallar o‘rtasida futbol turniri bo‘lib o‘tdi",
                    "A football tournament between the branches took place",
                ),
                "excerpt": T(
                    "Семь команд, один кубок и много эмоций: ученики всех филиалов "
                    "встретились на воскресном турнире.",
                    "Yetti jamoa, bitta kubok va ko‘plab his-hayajon: barcha filial "
                    "o‘quvchilari yakshanbalik turnirda uchrashdi.",
                    "Seven teams, one cup and plenty of emotion: students from every "
                    "branch met at the Sunday tournament.",
                ),
                "body": T(
                    "В воскресенье мы собрали учеников всех филиалов на большом "
                    "футбольном турнире. Семь команд, один кубок и целый день "
                    "поддержки, эмоций и командной игры.\n\n"
                    "Турнир прошёл в формате групповых матчей с выходом в плей-офф. "
                    "Ребята сами придумывали названия команд, готовили форму и "
                    "выбирали капитанов — а болеть за них пришли родители и "
                    "преподаватели.\n\n"
                    "Такие события — часть обучения в MARS IT School. Здесь ученики "
                    "учатся работать в команде, договариваться и поддерживать друг "
                    "друга: те же навыки, которые потом помогают им в проектах и "
                    "в реальной работе.\n\n"
                    "Следующий турнир пройдёт в конце сезона — следите за анонсами "
                    "в наших новостях и в платформе SPACE.",
                    "Yakshanba kuni barcha filial o‘quvchilarini katta futbol "
                    "turnirida to‘pladik. Yetti jamoa, bitta kubok va bir kunlik "
                    "qo‘llab-quvvatlash, hayajon va jamoaviy o‘yin.\n\n"
                    "Turnir guruh bosqichi va undan keyingi pley-off shaklida o‘tdi. "
                    "Bolalar jamoa nomlarini o‘zlari o‘ylab topishdi, forma tayyorlashdi "
                    "va sardor tanlashdi — ularni qo‘llab-quvvatlash uchun ota-onalar "
                    "va o‘qituvchilar kelishdi.\n\n"
                    "Bunday tadbirlar — MARS IT School’dagi ta’limning bir qismi. Bu "
                    "yerda o‘quvchilar jamoada ishlashni, kelishishni va bir-birini "
                    "qo‘llab-quvvatlashni o‘rganadi: aynan shu ko‘nikmalar keyinchalik "
                    "loyihalarda va haqiqiy ishda yordam beradi.\n\n"
                    "Keyingi turnir mavsum oxirida bo‘ladi — e’lonlarni yangiliklarimizda "
                    "va SPACE platformasida kuzatib boring.",
                    "On Sunday we brought together students from all our branches for a "
                    "big football tournament. Seven teams, one cup and a whole day of "
                    "support, emotion and team play.\n\n"
                    "The tournament ran as group matches followed by a play-off. The "
                    "children came up with their own team names, prepared kits and chose "
                    "captains — and parents and teachers came to cheer them on.\n\n"
                    "Events like this are part of learning at MARS IT School. Here "
                    "students learn to work in a team, to negotiate and to support each "
                    "other: the same skills that later help them in projects and in real "
                    "work.\n\n"
                    "The next tournament will be held at the end of the season — watch "
                    "for announcements in our news and on the SPACE platform.",
                ),
                "image": "news-football.webp",
                "reading_minutes": 3,
                "days_ago": 40,
                "category": events_category,
            },
            {
                "title": T(
                    "Demo Day: ученики представили 34 проекта",
                    "Demo Day: o‘quvchilar 34 ta loyihani taqdim etdi",
                    "Demo Day: students presented 34 projects",
                ),
                "excerpt": T(
                    "Сайты, Telegram-боты и умные устройства — родители и приглашённые "
                    "эксперты оценивали работы учеников.",
                    "Saytlar, Telegram-botlar va aqlli qurilmalar — o‘quvchilar ishlarini "
                    "ota-onalar va taklif etilgan ekspertlar baholadi.",
                    "Websites, Telegram bots and smart devices — parents and invited "
                    "experts assessed the students' work.",
                ),
                "body": T(
                    "Demo Day — день, когда ученики выходят на сцену и показывают то, "
                    "над чем работали весь модуль. В этот раз мы увидели 34 проекта: "
                    "сайты, Telegram-боты, игры и умные устройства на микроконтроллерах."
                    "\n\n"
                    "Каждая команда готовила короткую презентацию: какую задачу решает "
                    "проект, как он устроен и что было самым сложным. После выступления "
                    "ребята отвечали на вопросы приглашённых экспертов из IT-компаний."
                    "\n\n"
                    "Для многих это первый опыт публичного выступления — и он важен не "
                    "меньше кода. Умение объяснить свою идею простыми словами "
                    "пригодится и на защите проекта, и на будущем собеседовании.\n\n"
                    "Лучшие работы получили награды и попали в витрину проектов школы, "
                    "а все участники — обратную связь от экспертов.",
                    "Demo Day — o‘quvchilar sahnaga chiqib, butun modul davomida "
                    "ishlagan narsalarini ko‘rsatadigan kun. Bu safar biz 34 ta loyihani "
                    "ko‘rdik: saytlar, Telegram-botlar, o‘yinlar va mikrokontrollerlardagi "
                    "aqlli qurilmalar.\n\n"
                    "Har bir jamoa qisqa taqdimot tayyorladi: loyiha qanday masalani "
                    "yechadi, u qanday tuzilgan va eng qiyini nima bo‘ldi. Chiqishdan "
                    "so‘ng bolalar IT-kompaniyalardan taklif etilgan ekspertlarning "
                    "savollariga javob berishdi.\n\n"
                    "Ko‘pchilik uchun bu — omma oldida chiqishning ilk tajribasi va u "
                    "koddan kam ahamiyatli emas. O‘z g‘oyasini sodda so‘zlar bilan "
                    "tushuntira olish loyiha himoyasida ham, kelajakdagi suhbatda ham "
                    "asqotadi.\n\n"
                    "Eng yaxshi ishlar mukofot oldi va maktab loyihalari vitrinasiga "
                    "tushdi, barcha ishtirokchilar esa ekspertlardan fikr-mulohaza oldi.",
                    "Demo Day is the day when students take the stage and show what they "
                    "have worked on all module. This time we saw 34 projects: websites, "
                    "Telegram bots, games and smart devices built on microcontrollers.\n\n"
                    "Each team prepared a short presentation: what problem the project "
                    "solves, how it is built and what was hardest. After presenting, the "
                    "students answered questions from invited experts from IT companies."
                    "\n\n"
                    "For many this is their first experience of public speaking — and it "
                    "matters no less than the code. Being able to explain your idea in "
                    "simple words is useful both when defending a project and in a future "
                    "job interview.\n\n"
                    "The best works received awards and a place in the school's project "
                    "showcase, and every participant got feedback from the experts.",
                ),
                "image": "news-demoday.webp",
                "reading_minutes": 4,
                "days_ago": 48,
                "category": events_category,
            },
            {
                "title": T(
                    "Обновление платформы SPACE: сезонный рейтинг",
                    "SPACE platformasi yangilanishi: mavsumiy reyting",
                    "SPACE platform update: seasonal leaderboard",
                ),
                "excerpt": T(
                    "В SPACE стартовал новый сезон с обновлениями, которые сделают "
                    "обучение ещё увлекательнее.",
                    "SPACE’da o‘qishni yanada qiziqarli qiladigan yangilanishlar bilan "
                    "yangi mavsum boshlandi.",
                    "A new season has started in SPACE with updates that make learning "
                    "even more engaging.",
                ),
                "body": T(
                    "В SPACE стартовал новый сезон с обновлениями, которые сделают "
                    "обучение ещё динамичнее и интереснее. Теперь у каждого ученика "
                    "есть возможность не только прокачивать свои навыки, но и следить "
                    "за результатами, соревноваться и постепенно подниматься "
                    "в сезонном рейтинге.\n\n"
                    "В новом сезоне появились новые скины и элементы персонализации, "
                    "которые можно открывать по мере продвижения. А для тех, кто хочет "
                    "дополнительно потренироваться, мы добавили мини-игры для отработки "
                    "навыков набора кода. Они помогут улучшить скорость, внимательность "
                    "и точность, а заодно сделать привычную практику более "
                    "увлекательной.\n\n"
                    "Выполняйте задания, тренируйтесь, набирайте очки и следите за своим "
                    "местом в рейтинге. Каждый новый результат — это шаг вперёд "
                    "и возможность приблизиться к лидирующим позициям.\n\n"
                    "Сезон уже начался — заходите в SPACE, проверяйте свои навыки "
                    "и начинайте свой путь к вершине рейтинга!",
                    "SPACE’da o‘qishni yanada shiddatli va qiziqarli qiladigan "
                    "yangilanishlar bilan yangi mavsum boshlandi. Endi har bir o‘quvchi "
                    "nafaqat ko‘nikmalarini oshirishi, balki natijalarni kuzatishi, "
                    "musobaqalashishi va mavsumiy reytingda bosqichma-bosqich "
                    "ko‘tarilishi mumkin.\n\n"
                    "Yangi mavsumda yangi skinlar va shaxsiylashtirish elementlari paydo "
                    "bo‘ldi — ularni oldinga siljigan sari ochib borish mumkin. Qo‘shimcha "
                    "mashq qilmoqchi bo‘lganlar uchun esa kod terish ko‘nikmasini "
                    "mustahkamlaydigan mini-o‘yinlar qo‘shdik. Ular tezlik, diqqat va "
                    "aniqlikni oshiradi va odatiy amaliyotni qiziqarliroq qiladi.\n\n"
                    "Vazifalarni bajaring, mashq qiling, ball to‘plang va reytingdagi "
                    "o‘rningizni kuzatib boring. Har bir yangi natija — bu oldinga "
                    "qadam va yetakchi o‘rinlarga yaqinlashish imkoniyati.\n\n"
                    "Mavsum allaqachon boshlandi — SPACE’ga kiring, ko‘nikmalaringizni "
                    "sinab ko‘ring va reyting cho‘qqisiga yo‘lni boshlang!",
                    "A new season has started in SPACE with updates that make learning "
                    "even more dynamic and interesting. Now every student can not only "
                    "build up their skills but also track results, compete and gradually "
                    "climb the seasonal leaderboard.\n\n"
                    "The new season brings new skins and personalisation items that you "
                    "unlock as you progress. And for those who want extra practice, we "
                    "have added mini-games for drilling code-typing skills. They help "
                    "improve speed, attention and accuracy, while making routine practice "
                    "more fun.\n\n"
                    "Complete assignments, practise, earn points and watch your place in "
                    "the leaderboard. Every new result is a step forward and a chance to "
                    "get closer to the top.\n\n"
                    "The season has already begun — log in to SPACE, test your skills and "
                    "start your climb to the top of the leaderboard!",
                ),
                "image": "news-space.webp",
                "reading_minutes": 3,
                "days_ago": 59,
                "category": news_category,
            },
        ]

        for order, item in enumerate(items, 1):
            title, excerpt, body = item["title"], item["excerpt"], item["body"]
            news, created = News.objects.get_or_create(
                title_ru=title.ru,
                defaults={
                    "category": item["category"],
                    **title.fields("title"),
                    **excerpt.fields("excerpt"),
                    **body.fields("body"),
                    "published_at": timezone.now() - timedelta(days=item["days_ago"]),
                    "reading_minutes": item["reading_minutes"],
                    "is_featured": True,
                    "order": order,
                },
            )
            # Eski namunaviy yozuvlarda matn qisqa edi — to'liq matnga yangilaymiz.
            if not created and len(news.body_ru) < len(body.ru) // 2:
                news.category = item["category"]
                news.excerpt_ru = excerpt.ru
                news.body_ru = body.ru
                news.reading_minutes = item["reading_minutes"]
                news.save(update_fields=["category", "excerpt_ru", "body_ru", "reading_minutes"])

            self._fill_translations(news, title=title, excerpt=excerpt, body=body)
            attach_image(news, "cover", item["image"])

            # Fotoreportaj: bir marta yaratiladi (qayta ishga tushirilsa takrorlanmaydi).
            def caption_for(index: int, title: T = title) -> T:
                return T(
                    f"{title[0]} — {photo_caption[0]} {index}",
                    f"{title[1]} — {photo_caption[1]} {index}",
                    f"{title[2]} — {photo_caption[2]} {index}",
                )

            if news.gallery.exists():
                # Eski yozuvlarda izoh faqat ruscha edi — tarjimalarni to'ldiramiz.
                for image in news.gallery.order_by("order"):
                    self._fill_translations(image, caption=caption_for(image.order))
            else:
                for index, file_name in enumerate(gallery_pool, 1):
                    image = NewsImage.objects.create(
                        news=news,
                        **caption_for(index).fields("caption"),
                        order=index,
                    )
                    attach_image(image, "image", file_name)

    def _branches(self) -> None:
        branches = [
            {
                "name": T(
                    "Филиал на Амира Темура",
                    "Amir Temur filiali",
                    "Amir Temur branch",
                ),
                "address": T(
                    "Ташкент, ул. Амира Темура, 1",
                    "Toshkent, Amir Temur ko‘chasi, 1",
                    "Tashkent, Amir Temur street, 1",
                ),
                "phone": "+998 78 777 77 57",
                "latitude": 41.311081,
                "longitude": 69.240562,
                "is_main": True,
            },
            {
                "name": T("Филиал Tinchlik", "Tinchlik filiali", "Tinchlik branch"),
                "address": T(
                    "Ташкент, Шайхантахурский район, ул. Тинчлик, 12",
                    "Toshkent, Shayxontohur tumani, Tinchlik ko‘chasi, 12",
                    "Tashkent, Shaykhantakhur district, Tinchlik street, 12",
                ),
                "phone": "+998 78 777 77 58",
                "latitude": 41.325600,
                "longitude": 69.203100,
                "is_main": False,
            },
            {
                "name": T("Филиал Yunusabad", "Yunusobod filiali", "Yunusabad branch"),
                "address": T(
                    "Ташкент, Юнусабадский район, ул. Амира Темура, 108",
                    "Toshkent, Yunusobod tumani, Amir Temur ko‘chasi, 108",
                    "Tashkent, Yunusabad district, Amir Temur street, 108",
                ),
                "phone": "+998 78 777 77 59",
                "latitude": 41.347900,
                "longitude": 69.288900,
                "is_main": False,
            },
            {
                "name": T("Филиал Chilonzor", "Chilonzor filiali", "Chilanzar branch"),
                "address": T(
                    "Ташкент, Чиланзарский район, ул. Бунёдкор, 23",
                    "Toshkent, Chilonzor tumani, Bunyodkor ko‘chasi, 23",
                    "Tashkent, Chilanzar district, Bunyodkor street, 23",
                ),
                "phone": "+998 78 777 77 60",
                "latitude": 41.275300,
                "longitude": 69.204100,
                "is_main": False,
            },
            {
                "name": T(
                    "Филиал Максим Горький",
                    "Maksim Gorkiy filiali",
                    "Maxim Gorky branch",
                ),
                "address": T(
                    "Ташкент, Мирабадский район, ул. Махтумкули, 5",
                    "Toshkent, Mirobod tumani, Maxtumquli ko‘chasi, 5",
                    "Tashkent, Mirabad district, Makhtumkuli street, 5",
                ),
                "phone": "+998 78 777 77 61",
                "latitude": 41.299600,
                "longitude": 69.294800,
                "is_main": False,
            },
            {
                "name": T(
                    "Филиал Tashkent City",
                    "Tashkent City filiali",
                    "Tashkent City branch",
                ),
                "address": T(
                    "Ташкент, Яшнабадский район, ТРЦ Tashkent City Mall",
                    "Toshkent, Yashnobod tumani, Tashkent City Mall savdo markazi",
                    "Tashkent, Yashnabad district, Tashkent City Mall",
                ),
                "phone": "+998 78 777 77 62",
                "latitude": 41.308700,
                "longitude": 69.271500,
                "is_main": False,
            },
        ]

        for order, item in enumerate(branches, 1):
            name, address = item["name"], item["address"]
            branch, _created = Branch.objects.get_or_create(
                name_ru=name.ru,
                defaults={
                    **name.fields("name"),
                    **address.fields("address"),
                    **WORK_HOURS.fields("working_hours"),
                    "phone": item["phone"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "is_main": item["is_main"],
                    "order": order,
                },
            )
            self._fill_translations(branch, name=name, address=address, working_hours=WORK_HOURS)
            # Filial kartochkasidagi rasm — namunaviy foto.
            attach_image(branch, "cover", "news-demoday.webp")

    def _vacancies(self) -> None:
        # Eski namunaviy vakansiya endi ishlatilmaydi.
        Vacancy.objects.filter(title_ru="Преподаватель Python").delete()

        items = [
            {
                "title": T("Учитель", "O‘qituvchi", "Teacher"),
                "branch": "Филиал Tinchlik",
                "icon": Vacancy.Icon.CAP,
                "description": T(
                    "Ведёт группы по направлениям IT KIDS или Программирование.\n"
                    "Мы ищем преподавателя с практическим опытом в разработке "
                    "и желанием работать с детьми и подростками. Вы будете вести "
                    "занятия в небольших группах, помогать ученикам с проектами "
                    "и работать на платформе SPACE.",
                    "IT KIDS yoki Dasturlash yo‘nalishlarida guruhlarga dars beradi.\n"
                    "Biz ishlab chiqishda amaliy tajribaga ega va bolalar hamda "
                    "o‘smirlar bilan ishlashni istagan o‘qituvchini qidiryapmiz. Siz "
                    "kichik guruhlarda dars berasiz, o‘quvchilarga loyihalarda yordam "
                    "berasiz va SPACE platformasida ishlaysiz.",
                    "Teaches groups in the IT KIDS or Programming tracks.\n"
                    "We are looking for a teacher with hands-on development experience "
                    "who wants to work with children and teenagers. You will teach small "
                    "groups, help students with their projects and work on the SPACE "
                    "platform.",
                ),
                "requirements": T(
                    "Опыт коммерческой разработки от 2 лет.\n"
                    "Умение объяснять сложные темы простым языком.\n"
                    "Опыт работы с детьми будет преимуществом.",
                    "Tijorat loyihalarida 2 yildan ortiq ishlab chiqish tajribasi.\n"
                    "Murakkab mavzularni sodda tilda tushuntira olish.\n"
                    "Bolalar bilan ishlash tajribasi ustunlik bo‘ladi.",
                    "At least 2 years of commercial development experience.\n"
                    "The ability to explain complex topics in simple language.\n"
                    "Experience working with children is an advantage.",
                ),
                "conditions": T(
                    "Гибкий график и удобное расписание занятий.\n"
                    "Обучение методике преподавания за счёт школы.\n"
                    "Дружная команда и современные классы.",
                    "Moslashuvchan grafik va qulay dars jadvali.\n"
                    "O‘qitish metodikasi bo‘yicha maktab hisobidan tayyorgarlik.\n"
                    "Ahil jamoa va zamonaviy sinflar.",
                    "A flexible schedule and convenient class timetable.\n"
                    "Teacher-training methodology paid for by the school.\n"
                    "A friendly team and modern classrooms.",
                ),
            },
            {
                "title": T(
                    "Администратор филиала",
                    "Filial administratori",
                    "Branch administrator",
                ),
                "branch": "Филиал Yunusabad",
                "icon": Vacancy.Icon.BADGE,
                "description": T(
                    "Отвечает за работу филиала и коммуникацию с родителями.\n"
                    "Организация расписания, встреча учеников и родителей, контроль "
                    "порядка в классах, ведение отчётности филиала.",
                    "Filial ishi va ota-onalar bilan muloqot uchun javob beradi.\n"
                    "Jadvalni tashkil qilish, o‘quvchi va ota-onalarni kutib olish, "
                    "sinflardagi tartibni nazorat qilish, filial hisobotini yuritish.",
                    "Responsible for running the branch and communicating with parents.\n"
                    "Organising the timetable, welcoming students and parents, keeping "
                    "order in the classrooms and maintaining branch reporting.",
                ),
                "requirements": T(
                    "Опыт работы с людьми от 1 года.\n"
                    "Внимательность к деталям и организованность.\n"
                    "Уверенное владение компьютером.",
                    "Odamlar bilan ishlashda 1 yildan ortiq tajriba.\n"
                    "Tafsilotlarga e’tibor va uyushqoqlik.\n"
                    "Kompyuterni ishonchli bilish.",
                    "At least 1 year of experience working with people.\n"
                    "Attention to detail and strong organisation.\n"
                    "Confident computer skills.",
                ),
                "conditions": T(
                    "Полная занятость, стабильный график.\nОформление и обучение внутри школы.",
                    "To‘liq bandlik, barqaror grafik.\nRasmiylashtirish va maktab ichida o‘qitish.",
                    "Full-time work with a stable schedule.\n"
                    "Official employment and in-house training.",
                ),
            },
            {
                "title": T("Куратор", "Kurator", "Curator"),
                "branch": "Филиал Chilonzor",
                "icon": Vacancy.Icon.USERS,
                "description": T(
                    "Сопровождает группы и следит за прогрессом учеников.\n"
                    "Помогает преподавателю на занятиях, поддерживает связь "
                    "с родителями, контролирует выполнение домашних заданий "
                    "на платформе SPACE.",
                    "Guruhlarni kuzatib boradi va o‘quvchilar taraqqiyotini nazorat "
                    "qiladi.\nDarslarda o‘qituvchiga yordam beradi, ota-onalar bilan "
                    "aloqani saqlaydi, SPACE platformasida uy vazifalari bajarilishini "
                    "nazorat qiladi.",
                    "Supports the groups and tracks student progress.\n"
                    "Helps the teacher in class, keeps in touch with parents and checks "
                    "that homework is completed on the SPACE platform.",
                ),
                "requirements": T(
                    "Любовь к работе с детьми и подростками.\n"
                    "Ответственность и умение вести коммуникацию.",
                    "Bolalar va o‘smirlar bilan ishlashni yoqtirish.\n"
                    "Mas’uliyat va muloqot qura olish.",
                    "A love of working with children and teenagers.\n"
                    "Responsibility and good communication skills.",
                ),
                "conditions": T(
                    "Частичная занятость, возможен совмещённый график.\n"
                    "Рост до преподавателя внутри школы.",
                    "Yarim bandlik, birgalikda olib borish mumkin.\n"
                    "Maktab ichida o‘qituvchilikkacha o‘sish.",
                    "Part-time work, can be combined with other commitments.\n"
                    "Growth into a teaching role within the school.",
                ),
                "employment": Vacancy.Employment.PART_TIME,
            },
            {
                "title": T(
                    "Оператор колл-центра",
                    "Kol-markaz operatori",
                    "Call centre operator",
                ),
                "branch": "Филиал Максим Горький",
                "icon": Vacancy.Icon.HEADSET,
                "description": T(
                    "Работает с входящими заявками и записью на пробные уроки.\n"
                    "Обработка заявок с сайта и рекламы, консультация родителей "
                    "по курсам, запись на пробные занятия, работа в CRM.",
                    "Kelib tushgan arizalar va sinov darsiga yozilish bilan ishlaydi.\n"
                    "Sayt va reklamadan kelgan arizalarni qayta ishlash, ota-onalarga "
                    "kurslar bo‘yicha maslahat, sinov darsiga yozish, CRM’da ishlash.",
                    "Handles incoming enquiries and trial-lesson bookings.\n"
                    "Processing requests from the website and adverts, advising parents "
                    "on courses, booking trial lessons and working in the CRM.",
                ),
                "requirements": T(
                    "Грамотная речь на русском и узбекском языках.\n"
                    "Опыт работы с CRM будет преимуществом.",
                    "Rus va o‘zbek tillarida savodli nutq.\n"
                    "CRM bilan ishlash tajribasi ustunlik bo‘ladi.",
                    "Articulate speech in Russian and Uzbek.\n"
                    "Experience with a CRM is an advantage.",
                ),
                "conditions": T(
                    "Полная занятость, сменный график.\nОбучение продукту и скриптам общения.",
                    "To‘liq bandlik, smenali grafik.\n"
                    "Mahsulot va muloqot skriptlari bo‘yicha o‘qitish.",
                    "Full-time work on a shift schedule.\n"
                    "Training on the product and conversation scripts.",
                ),
            },
        ]

        for order, item in enumerate(items, 1):
            title = item["title"]
            description, requirements = item["description"], item["requirements"]
            conditions = item["conditions"]
            vacancy, _ = Vacancy.objects.get_or_create(
                title_ru=title.ru,
                defaults={
                    "branch": Branch.objects.filter(name_ru=item["branch"]).first(),
                    **title.fields("title"),
                    **description.fields("description"),
                    **requirements.fields("requirements"),
                    **conditions.fields("conditions"),
                    "employment_type": item.get("employment", Vacancy.Employment.FULL_TIME),
                    "icon_name": item["icon"],
                    "order": order,
                },
            )
            self._fill_translations(
                vacancy,
                title=title,
                description=description,
                requirements=requirements,
                conditions=conditions,
            )

    def _quiz(self, courses: list[Course]) -> None:
        """Proforientatsiya testi — savollar bazasi `apps/quiz/seeding.py` da."""
        del courses  # kurslar natijalarga `ensure_quiz` ichida bog'lanadi
        ensure_quiz()

    def _reviews(self) -> None:
        for order, (name, relation, text, image) in enumerate(REVIEWS, 1):
            review, _ = ParentReview.objects.get_or_create(
                full_name=name,
                defaults={
                    **relation.fields("relation"),
                    **text.fields("text"),
                    "order": order,
                    "video_url": "https://youtu.be/",
                },
            )
            self._fill_translations(review, relation=relation, text=text)
            attach_image(review, "photo", image)
