"""Proforientatsiya testining savollar bazasi va uni yaratish funksiyasi.

Test ikkita natijadan birini beradi: **Frontend** (ko'rinadigan qism — dizayn,
interfeys, animatsiya) yoki **Backend** (ko'rinmas qism — ma'lumotlar, mantiq,
server, xavfsizlik).

Har bir javob varianti bitta ko'nikmani ham ko'rsatadi (`QUESTION_SKILLS`) —
natija sahifasidagi «Qobiliyatlar tahlili» diagrammasi shundan yig'iladi.

Savollar bazasi 30 ta — foydalanuvchiga har safar shundan 20 tasi tasodifiy
ko'rsatiladi (`Quiz.questions_per_attempt`). Har bir javob varianti bitta
yo'nalishga ball qo'shadi: `weight = 2` — kuchli belgi, `1` — kuchsizroq.

Barcha matnlar uch tilda (`T(ru, uz, en)`) — test uz/ru/en da bir xil ishlashi
uchun. Bo'sh tarjima qolsa, API asosiy tilga (ru) qaytadi.
"""

from .models import Option, Outcome, Question, Quiz


class T(tuple):
    """Uch tilli matn: `T("ru", "uz", "en")` → `fields("text")` lug'at beradi."""

    __slots__ = ()

    def __new__(cls, ru: str, uz: str, en: str):
        return super().__new__(cls, (ru, uz, en))

    def fields(self, name: str) -> dict[str, str]:
        return {f"{name}_ru": self[0], f"{name}_uz": self[1], f"{name}_en": self[2]}

    @property
    def ru(self) -> str:
        return self[0]


QUIZ_SLUG = "proforientatsiya"

QUIZ_TITLE = T(
    "Какое направление выбрать?",
    "Qaysi yo‘nalishni tanlash kerak?",
    "Which track should you choose?",
)
QUIZ_DESCRIPTION = T(
    "Ответьте на несколько вопросов, чтобы узнать, какое направление разработки "
    "будет интересно и полезно вашему ребёнку.",
    "Farzandingizga dasturlashning qaysi yo‘nalishi qiziqarli va foydali "
    "bo‘lishini bilish uchun bir necha savolga javob bering.",
    "Answer a few questions to find out which development track will be "
    "interesting and useful for your child.",
)

#: `code` — Option.outcome kodi, `title` — natija sahifasidagi sarlavha.
OUTCOMES = [
    (
        "frontend",
        T("Frontend", "Frontend", "Frontend"),
        T(
            "Вам ближе видимая часть продукта: интерфейсы, вёрстка, анимации и то, "
            "как человек пользуется сайтом или приложением.",
            "Sizga mahsulotning ko‘rinadigan qismi yaqinroq: interfeyslar, "
            "verstka, animatsiyalar va inson sayt yoki ilovadan qanday "
            "foydalanishi.",
            "You are drawn to the visible part of a product: interfaces, layout, "
            "animation and how a person uses a site or app.",
        ),
    ),
    (
        "backend",
        T("Backend", "Backend", "Backend"),
        T(
            "Вам ближе внутренняя часть продукта: данные, логика, серверы, "
            "безопасность и то, как всё это работает под капотом.",
            "Sizga mahsulotning ichki qismi yaqinroq: ma’lumotlar, mantiq, "
            "serverlar, xavfsizlik va bularning hammasi ichkarida qanday ishlashi.",
            "You are drawn to the inner part of a product: data, logic, servers, "
            "security and how it all works under the hood.",
        ),
    ),
]

#: (savol, [(javob, natija kodi, ball), ...]) — hammasi uch tilda.
QUESTIONS = [
    (
        T(
            "Что вы любите делать в свободное время?",
            "Bo‘sh vaqtingizda nima qilishni yoqtirasiz?",
            "What do you like doing in your free time?",
        ),
        [
            (
                T(
                    "Рисовать или заниматься дизайном",
                    "Rasm chizish yoki dizayn bilan shug‘ullanish",
                    "Drawing or design",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Решать математические задачи",
                    "Matematik masalalar yechish",
                    "Solving maths problems",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Снимать и монтировать видео",
                    "Video suratga olish va montaj qilish",
                    "Shooting and editing video",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Внимательно разбираться в чём-то одном",
                    "Bitta narsani sinchiklab o‘rganish",
                    "Digging deeply into one thing",
                ),
                "backend",
                1,
            ),
        ],
    ),
    (
        T(
            "Что первым замечаете на сайте?",
            "Saytda birinchi bo‘lib nimani sezasiz?",
            "What do you notice first on a website?",
        ),
        [
            (
                T(
                    "Цвета, шрифты и оформление",
                    "Ranglar, shriftlar va bezak",
                    "Colours, fonts and styling",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Удобно ли всё расположено",
                    "Hammasi qulay joylashganmi",
                    "Whether everything is laid out conveniently",
                ),
                "frontend",
                1,
            ),
            (T("Быстро ли он работает", "Tez ishlaydimi", "Whether it works fast"), "backend", 1),
            (
                T(
                    "Как устроен поиск и данные",
                    "Qidiruv va ma’lumotlar qanday tuzilgan",
                    "How the search and data are built",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что интереснее сделать?",
            "Nimani yasash qiziqroq?",
            "Which would be more interesting to build?",
        ),
        [
            (
                T(
                    "Красивую кнопку с анимацией",
                    "Animatsiyali chiroyli tugma",
                    "A beautiful animated button",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Страницу, которая хорошо смотрится на телефоне",
                    "Telefonda chiroyli ko‘rinadigan sahifa",
                    "A page that looks great on a phone",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Систему, которая считает заказы",
                    "Buyurtmalarni hisoblaydigan tizim",
                    "A system that counts orders",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Бота, который отвечает на сообщения",
                    "Xabarlarga javob beradigan bot",
                    "A bot that replies to messages",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Какая часть работы кажется приятнее?",
            "Ishning qaysi qismi yoqimliroq tuyuladi?",
            "Which part of the work feels more enjoyable?",
        ),
        [
            (
                T(
                    "Видеть результат сразу на экране",
                    "Natijani darrov ekranda ko‘rish",
                    "Seeing the result on screen right away",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Подбирать оформление под идею",
                    "G‘oyaga mos bezak tanlash",
                    "Choosing a style to match the idea",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Придумывать логику решения",
                    "Yechim mantiqini o‘ylab topish",
                    "Working out the logic of a solution",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Наводить порядок в данных",
                    "Ma’lumotlarda tartib o‘rnatish",
                    "Bringing order to data",
                ),
                "backend",
                1,
            ),
        ],
    ),
    (
        T(
            "Что ближе к вашему характеру?",
            "Fe’lingizga nima yaqinroq?",
            "What is closer to your character?",
        ),
        [
            (
                T(
                    "Люблю, когда красиво",
                    "Chiroyli bo‘lishini yoqtiraman",
                    "I like things to look beautiful",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Замечаю мелкие детали оформления",
                    "Bezakdagi mayda tafsilotlarni sezaman",
                    "I notice small styling details",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Люблю, когда всё логично",
                    "Hammasi mantiqli bo‘lishini yoqtiraman",
                    "I like it when everything is logical",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Люблю доводить систему до порядка",
                    "Tizimni tartibga keltirishni yoqtiraman",
                    "I like getting a system in order",
                ),
                "backend",
                1,
            ),
        ],
    ),
    (
        T(
            "Какой школьный предмет нравится больше?",
            "Maktabda qaysi fan ko‘proq yoqadi?",
            "Which school subject do you like most?",
        ),
        [
            (T("Рисование", "Tasviriy san’at", "Art"), "frontend", 2),
            (
                T("Литература и языки", "Adabiyot va tillar", "Literature and languages"),
                "frontend",
                1,
            ),
            (T("Математика", "Matematika", "Maths"), "backend", 2),
            (T("Физика", "Fizika", "Physics"), "backend", 1),
        ],
    ),
    (
        T(
            "Что бы вы выбрали в командном проекте?",
            "Jamoaviy loyihada nimani tanlagan bo‘lardingiz?",
            "What would you choose in a team project?",
        ),
        [
            (
                T(
                    "Сделать внешний вид приложения",
                    "Ilovaning tashqi ko‘rinishini yasash",
                    "Building the app's look",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Нарисовать макет и иконки",
                    "Maket va ikonkalar chizish",
                    "Drawing the layout and icons",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Настроить базу данных",
                    "Ma’lumotlar bazasini sozlash",
                    "Setting up the database",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Написать логику расчётов",
                    "Hisob-kitob mantiqini yozish",
                    "Writing the calculation logic",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что интереснее в играх?",
            "O‘yinlarda nima qiziqroq?",
            "What is more interesting in games?",
        ),
        [
            (
                T(
                    "Внешний вид персонажей и уровней",
                    "Qahramonlar va bosqichlar ko‘rinishi",
                    "The look of characters and levels",
                ),
                "frontend",
                2,
            ),
            (T("Интерфейс и меню", "Interfeys va menyu", "The interface and menus"), "frontend", 1),
            (T("Правила и баланс", "Qoidalar va muvozanat", "Rules and balance"), "backend", 2),
            (
                T(
                    "Как считаются очки и рейтинг",
                    "Ballar va reyting qanday hisoblanadi",
                    "How points and rankings are calculated",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Как вы относитесь к работе с цветом и типографикой?",
            "Rang va tipografika bilan ishlashga munosabatingiz qanday?",
            "How do you feel about working with colour and typography?",
        ),
        [
            (
                T(
                    "Очень нравится подбирать",
                    "Tanlash juda yoqadi",
                    "I really enjoy choosing them",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Интересно, но нужна помощь",
                    "Qiziq, lekin yordam kerak",
                    "Interesting, but I need help",
                ),
                "frontend",
                1,
            ),
            (T("Скучновато", "Biroz zerikarli", "A bit boring"), "backend", 1),
            (
                T(
                    "Лучше займусь кодом логики",
                    "Yaxshisi mantiq kodi bilan shug‘ullanaman",
                    "I would rather work on logic code",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что скажете про таблицы и данные?",
            "Jadval va ma’lumotlar haqida nima deysiz?",
            "What do you think about tables and data?",
        ),
        [
            (
                T("Стараюсь избегать", "Chetlab o‘tishga harakat qilaman", "I try to avoid them"),
                "frontend",
                2,
            ),
            (
                T("Работаю, если нужно", "Kerak bo‘lsa ishlayman", "I work with them if I have to"),
                "frontend",
                1,
            ),
            (
                T(
                    "Нравится наводить в них порядок",
                    "Ularda tartib o‘rnatish yoqadi",
                    "I like bringing order to them",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Люблю искать закономерности",
                    "Qonuniyat izlashni yoqtiraman",
                    "I like looking for patterns",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Какая ошибка раздражает сильнее?",
            "Qaysi xato ko‘proq asabiylashtiradi?",
            "Which mistake annoys you more?",
        ),
        [
            (
                T(
                    "Кнопка съехала и выглядит криво",
                    "Tugma siljib, qiyshiq ko‘rinadi",
                    "A button has shifted and looks crooked",
                ),
                "frontend",
                2,
            ),
            (
                T("Текст плохо читается", "Matn yaxshi o‘qilmaydi", "The text is hard to read"),
                "frontend",
                1,
            ),
            (
                T(
                    "Данные сохранились неправильно",
                    "Ma’lumot noto‘g‘ri saqlandi",
                    "The data was saved incorrectly",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Страница долго загружается",
                    "Sahifa uzoq yuklanadi",
                    "The page takes a long time to load",
                ),
                "backend",
                1,
            ),
        ],
    ),
    (
        T(
            "Что хочется показать друзьям?",
            "Do‘stlarga nimani ko‘rsatgingiz keladi?",
            "What would you want to show your friends?",
        ),
        [
            (
                T(
                    "Красивую страницу, которую сделали сами",
                    "O‘zingiz yasagan chiroyli sahifani",
                    "A beautiful page you built yourself",
                ),
                "frontend",
                2,
            ),
            (
                T("Анимацию или эффект", "Animatsiya yoki effektni", "An animation or effect"),
                "frontend",
                2,
            ),
            (T("Бота в Telegram", "Telegram’dagi botni", "A Telegram bot"), "backend", 2),
            (
                T(
                    "Сервис, который считает что-то полезное",
                    "Foydali narsani hisoblaydigan xizmatni",
                    "A service that calculates something useful",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Как вам ближе учиться новому?",
            "Yangi narsani qanday o‘rganish sizga yaqinroq?",
            "How do you prefer to learn something new?",
        ),
        [
            (
                T(
                    "Повторять за примером и менять оформление",
                    "Namunani takrorlab, bezakni o‘zgartirish",
                    "Following an example and changing the styling",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Смотреть, как делают другие",
                    "Boshqalar qanday qilishini kuzatish",
                    "Watching how others do it",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Разбирать, как это устроено внутри",
                    "Ichkarida qanday tuzilganini o‘rganish",
                    "Taking apart how it works inside",
                ),
                "backend",
                2,
            ),
            (
                T("Читать документацию", "Hujjatlarni o‘qish", "Reading the documentation"),
                "backend",
                1,
            ),
        ],
    ),
    (
        T(
            "Что интереснее исправлять?",
            "Nimani tuzatish qiziqroq?",
            "What is more interesting to fix?",
        ),
        [
            (
                T(
                    "Вёрстку, которая ломается на телефоне",
                    "Telefonda buziladigan verstkani",
                    "Layout that breaks on a phone",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Некрасивые отступы и шрифты",
                    "Xunuk bo‘shliq va shriftlarni",
                    "Ugly spacing and fonts",
                ),
                "frontend",
                1,
            ),
            (
                T("Ошибку в расчётах", "Hisob-kitobdagi xatoni", "An error in the calculations"),
                "backend",
                2,
            ),
            (
                T("Медленный запрос к базе", "Bazaga sekin so‘rovni", "A slow database query"),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что для вас важнее в приложении?",
            "Ilovada siz uchun nima muhimroq?",
            "What matters more to you in an app?",
        ),
        [
            (
                T(
                    "Чтобы им было приятно пользоваться",
                    "Foydalanish yoqimli bo‘lishi",
                    "That it is pleasant to use",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Чтобы всё было понятно с первого взгляда",
                    "Hammasi bir qarashda tushunarli bo‘lishi",
                    "That everything is clear at a glance",
                ),
                "frontend",
                1,
            ),
            (
                T("Чтобы данные не терялись", "Ma’lumot yo‘qolmasligi", "That data is never lost"),
                "backend",
                2,
            ),
            (
                T(
                    "Чтобы выдерживало много пользователей",
                    "Ko‘p foydalanuvchiga bardosh berishi",
                    "That it handles many users",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Как вы относитесь к математике и логике?",
            "Matematika va mantiqqa munosabatingiz qanday?",
            "How do you feel about maths and logic?",
        ),
        [
            (T("Нейтрально", "Befarq", "Neutral"), "frontend", 1),
            (
                T("Больше нравится творчество", "Ijod ko‘proq yoqadi", "I prefer creative work"),
                "frontend",
                2,
            ),
            (
                T("Нравится решать задачи", "Masala yechish yoqadi", "I enjoy solving problems"),
                "backend",
                2,
            ),
            (
                T(
                    "Люблю логические головоломки",
                    "Mantiqiy boshqotirmalarni yoqtiraman",
                    "I love logic puzzles",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что бы вы улучшили в любимом сайте?",
            "Sevimli saytingizda nimani yaxshilagan bo‘lardingiz?",
            "What would you improve on your favourite site?",
        ),
        [
            (T("Дизайн и оформление", "Dizayn va bezak", "The design and styling"), "frontend", 2),
            (T("Удобство навигации", "Navigatsiya qulayligi", "Ease of navigation"), "frontend", 1),
            (T("Скорость работы", "Ishlash tezligi", "Its speed"), "backend", 1),
            (T("Поиск и фильтры", "Qidiruv va filtrlar", "Search and filters"), "backend", 2),
        ],
    ),
    (
        T(
            "Какой результат приятнее?",
            "Qaysi natija yoqimliroq?",
            "Which kind of result feels better?",
        ),
        [
            (
                T(
                    "Видно глазами сразу",
                    "Ko‘z bilan darrov ko‘rinadi",
                    "You can see it immediately",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Можно показать на экране телефона",
                    "Telefon ekranida ko‘rsatish mumkin",
                    "You can show it on a phone screen",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Работает незаметно, но правильно",
                    "Sezilmay, lekin to‘g‘ri ishlaydi",
                    "It works invisibly but correctly",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Экономит время другим",
                    "Boshqalarning vaqtini tejaydi",
                    "It saves other people time",
                ),
                "backend",
                1,
            ),
        ],
    ),
    (
        T(
            "Что вам ближе в фотографии?",
            "Fotografiyada sizga nima yaqinroq?",
            "What appeals to you more in photography?",
        ),
        [
            (
                T(
                    "Композиция и обработка",
                    "Kompozitsiya va qayta ishlash",
                    "Composition and editing",
                ),
                "frontend",
                2,
            ),
            (T("Подбор цвета", "Rang tanlash", "Colour grading"), "frontend", 1),
            (T("Настройки техники", "Texnika sozlamalari", "Camera settings"), "backend", 1),
            (
                T(
                    "Как устроена камера внутри",
                    "Kamera ichkarida qanday tuzilgan",
                    "How a camera works inside",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Как вы планируете работу?",
            "Ishni qanday rejalashtirasiz?",
            "How do you plan your work?",
        ),
        [
            (
                T(
                    "Сначала рисую, как всё будет выглядеть",
                    "Avval hammasi qanday ko‘rinishini chizaman",
                    "First I sketch how it will look",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Начинаю с внешнего вида",
                    "Tashqi ko‘rinishdan boshlayman",
                    "I start with the appearance",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Сначала продумываю структуру",
                    "Avval tuzilmani o‘ylab olaman",
                    "First I think through the structure",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Начинаю с данных и правил",
                    "Ma’lumot va qoidalardan boshlayman",
                    "I start with the data and rules",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что интереснее изучать?",
            "Nimani o‘rganish qiziqroq?",
            "What is more interesting to learn?",
        ),
        [
            (T("HTML и CSS", "HTML va CSS", "HTML and CSS"), "frontend", 2),
            (
                T(
                    "Анимации в интерфейсах",
                    "Interfeysdagi animatsiyalar",
                    "Animation in interfaces",
                ),
                "frontend",
                2,
            ),
            (T("Базы данных", "Ma’lumotlar bazalari", "Databases"), "backend", 2),
            (T("Алгоритмы", "Algoritmlar", "Algorithms"), "backend", 2),
        ],
    ),
    (
        T(
            "Как относитесь к безопасности данных?",
            "Ma’lumotlar xavfsizligiga munosabatingiz qanday?",
            "How do you feel about data security?",
        ),
        [
            (
                T(
                    "Слышал, но не углублялся",
                    "Eshitganman, lekin chuqurlashmaganman",
                    "I have heard of it but not gone deep",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Мне интереснее внешний вид",
                    "Menga tashqi ko‘rinish qiziqroq",
                    "The appearance interests me more",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Интересно, как защищают пароли",
                    "Parollar qanday himoyalanishi qiziq",
                    "I am curious how passwords are protected",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Хочу разобраться в этом глубже",
                    "Buni chuqurroq o‘rganmoqchiman",
                    "I want to understand it more deeply",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что бы вы сделали для школы?",
            "Maktab uchun nima qilgan bo‘lardingiz?",
            "What would you build for your school?",
        ),
        [
            (
                T(
                    "Красивый сайт с расписанием",
                    "Dars jadvali bor chiroyli sayt",
                    "A beautiful site with the timetable",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Оформление и иллюстрации",
                    "Bezak va illyustratsiyalar",
                    "Styling and illustrations",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Систему учёта посещаемости",
                    "Davomatni hisobga olish tizimi",
                    "An attendance tracking system",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Бота для ответов на вопросы",
                    "Savollarga javob beradigan bot",
                    "A bot that answers questions",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что вам легче даётся?",
            "Sizga nima osonroq beriladi?",
            "What comes more easily to you?",
        ),
        [
            (
                T(
                    "Замечать, что выглядит неаккуратно",
                    "Nima ozoda ko‘rinmasligini sezish",
                    "Noticing what looks untidy",
                ),
                "frontend",
                2,
            ),
            (
                T("Придумывать оформление", "Bezak o‘ylab topish", "Coming up with a design"),
                "frontend",
                1,
            ),
            (
                T(
                    "Находить ошибку в рассуждении",
                    "Mulohazadagi xatoni topish",
                    "Finding the flaw in an argument",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Держать в голове сложную схему",
                    "Murakkab sxemani yodda saqlash",
                    "Holding a complex scheme in your head",
                ),
                "backend",
                1,
            ),
        ],
    ),
    (
        T(
            "Какой отзыв о вашей работе приятнее услышать?",
            "Ishingiz haqida qanday fikr eshitish yoqimliroq?",
            "Which feedback about your work would you rather hear?",
        ),
        [
            (
                T(
                    "«Как красиво и удобно!»",
                    "«Qanday chiroyli va qulay!»",
                    "“How beautiful and convenient!”",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "«Сразу понятно, куда нажимать»",
                    "«Qayerga bosishni darrov tushunsa bo‘ladi»",
                    "“It is immediately clear where to click”",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "«Всё работает быстро и точно»",
                    "«Hammasi tez va aniq ishlaydi»",
                    "“Everything works fast and accurately”",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "«Ничего не сломалось при нагрузке»",
                    "«Yuklama ostida hech narsa buzilmadi»",
                    "“Nothing broke under load”",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что интереснее в мобильном приложении?",
            "Mobil ilovada nima qiziqroq?",
            "What is more interesting in a mobile app?",
        ),
        [
            (
                T(
                    "Экраны и переходы между ними",
                    "Ekranlar va ular orasidagi o‘tishlar",
                    "Screens and the transitions between them",
                ),
                "frontend",
                2,
            ),
            (
                T("Тёмная тема и оформление", "Tungi rejim va bezak", "Dark mode and styling"),
                "frontend",
                1,
            ),
            (
                T("Синхронизация данных", "Ma’lumotlar sinxronizatsiyasi", "Data synchronisation"),
                "backend",
                2,
            ),
            (T("Работа без интернета", "Internetsiz ishlash", "Working offline"), "backend", 1),
        ],
    ),
    (
        T(
            "Как вы поступите, если задача большая?",
            "Vazifa katta bo‘lsa nima qilasiz?",
            "What do you do when a task is large?",
        ),
        [
            (
                T(
                    "Начну с той части, которую видно",
                    "Ko‘rinadigan qismidan boshlayman",
                    "I start with the visible part",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Сначала соберу внешний вид",
                    "Avval tashqi ko‘rinishni yig‘aman",
                    "First I assemble the appearance",
                ),
                "frontend",
                1,
            ),
            (
                T(
                    "Разобью на этапы и продумаю логику",
                    "Bosqichlarga bo‘lib, mantiqni o‘ylayman",
                    "I break it into stages and think through the logic",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Начну с данных, потом остальное",
                    "Ma’lumotdan boshlab, keyin qolganini",
                    "I start with the data, then the rest",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что ближе: инструменты дизайна или консоль?",
            "Qaysi biri yaqin: dizayn vositalari yoki konsol?",
            "Which is closer: design tools or the console?",
        ),
        [
            (
                T(
                    "Figma и графические редакторы",
                    "Figma va grafik muharrirlar",
                    "Figma and graphics editors",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Редактор с готовым результатом на экране",
                    "Natija darrov ekranda ko‘rinadigan muharrir",
                    "An editor that shows the result on screen",
                ),
                "frontend",
                1,
            ),
            (
                T("Терминал и команды", "Terminal va buyruqlar", "The terminal and commands"),
                "backend",
                2,
            ),
            (
                T(
                    "Инструменты для работы с базой",
                    "Baza bilan ishlash vositalari",
                    "Tools for working with a database",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Что вас больше увлекает?",
            "Sizni nima ko‘proq qiziqtiradi?",
            "What fascinates you more?",
        ),
        [
            (
                T(
                    "Как человек воспринимает интерфейс",
                    "Inson interfeysni qanday qabul qilishi",
                    "How a person perceives an interface",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Как сделать сложное простым на вид",
                    "Murakkabni ko‘rinishda sodda qilish",
                    "How to make something complex look simple",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Как устроены большие системы",
                    "Katta tizimlar qanday tuzilgani",
                    "How large systems are built",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Как ускорить обработку данных",
                    "Ma’lumotlarni qayta ishlashni tezlatish",
                    "How to speed up data processing",
                ),
                "backend",
                2,
            ),
        ],
    ),
    (
        T(
            "Кем интереснее быть в проекте?",
            "Loyihada kim bo‘lish qiziqroq?",
            "Which role in a project appeals more?",
        ),
        [
            (
                T(
                    "Тем, кто делает продукт красивым",
                    "Mahsulotni chiroyli qiladigan kishi",
                    "The one who makes the product beautiful",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Тем, кто отвечает за удобство",
                    "Qulaylik uchun javob beradigan kishi",
                    "The one responsible for usability",
                ),
                "frontend",
                2,
            ),
            (
                T(
                    "Тем, кто отвечает за надёжность",
                    "Ishonchlilik uchun javob beradigan kishi",
                    "The one responsible for reliability",
                ),
                "backend",
                2,
            ),
            (
                T(
                    "Тем, кто строит логику работы",
                    "Ishlash mantiqini quradigan kishi",
                    "The one who builds the working logic",
                ),
                "backend",
                2,
            ),
        ],
    ),
]

#: Har bir savolning to'rt javobi qaysi ko'nikmani ko'rsatadi (`QUESTIONS` bilan
#: bir tartibda). Ko'nikmalar natija sahifasidagi «Анализ способностей» blokini
#: yig'adi — shuning uchun har bir variantga aniq bittasi biriktiriladi.
QUESTION_SKILLS = [
    ("creativity", "math", "communication", "patience"),
    ("visual", "creativity", "accuracy", "logic"),
    ("creativity", "visual", "logic", "math"),
    ("visual", "creativity", "logic", "accuracy"),
    ("creativity", "visual", "logic", "accuracy"),
    ("creativity", "communication", "math", "logic"),
    ("visual", "creativity", "accuracy", "logic"),
    ("visual", "creativity", "logic", "math"),
    ("creativity", "visual", "accuracy", "logic"),
    ("creativity", "patience", "accuracy", "math"),
    ("visual", "creativity", "accuracy", "logic"),
    ("visual", "creativity", "logic", "math"),
    ("visual", "social", "logic", "patience"),
    ("visual", "accuracy", "math", "logic"),
    ("creativity", "visual", "accuracy", "logic"),
    ("patience", "creativity", "math", "logic"),
    ("creativity", "visual", "accuracy", "logic"),
    ("visual", "social", "accuracy", "logic"),
    ("creativity", "visual", "accuracy", "logic"),
    ("visual", "creativity", "logic", "accuracy"),
    ("visual", "creativity", "accuracy", "logic"),
    ("social", "creativity", "logic", "patience"),
    ("visual", "creativity", "accuracy", "logic"),
    ("visual", "creativity", "logic", "patience"),
    ("creativity", "communication", "accuracy", "logic"),
    ("visual", "creativity", "accuracy", "logic"),
    ("visual", "creativity", "patience", "logic"),
    ("creativity", "visual", "logic", "accuracy"),
    ("communication", "creativity", "logic", "math"),
    ("creativity", "communication", "accuracy", "logic"),
]


def _fill_translations(instance, **texts) -> None:
    """Mavjud yozuvdagi bo'sh `_uz` / `_en` maydonlarini to'ldiradi.

    Admin panelda yozilgan matn hech qachon qayta yozilmaydi — faqat
    bo'sh tarjimalar to'ldiriladi, shunda eski baza ham uch tilli bo'ladi.
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


def ensure_quiz(*, reset: bool = False) -> Quiz:
    """Testni, natijalarni va savollar bazasini yaratadi (idempotent).

    Mavjud yozuvlar o'zgartirilmaydi — faqat yetishmaydiganlari qo'shiladi,
    shuning uchun buyruqni xohlagancha qayta ishga tushirish mumkin. Bo'sh
    qolgan `_uz` / `_en` tarjimalari har safar to'ldiriladi.

    `reset=True` — eski savollar va natijalar o'chirilib, baza qaytadan
    yig'iladi (yo'nalishlar ro'yxati o'zgarganda kerak bo'ladi).
    """
    quiz, created = Quiz.objects.get_or_create(
        slug=QUIZ_SLUG,
        defaults={
            **QUIZ_TITLE.fields("title"),
            **QUIZ_DESCRIPTION.fields("description"),
            "questions_per_attempt": 20,
        },
    )
    if not created and not quiz.questions_per_attempt:
        quiz.questions_per_attempt = 20
        quiz.save(update_fields=["questions_per_attempt"])
    _fill_translations(quiz, title=QUIZ_TITLE, description=QUIZ_DESCRIPTION)

    if reset:
        Question.objects.filter(quiz=quiz).delete()
        Outcome.objects.filter(quiz=quiz).delete()

    outcomes: dict[str, Outcome] = {}
    for code, title, description in OUTCOMES:
        outcome, _ = Outcome.objects.get_or_create(
            quiz=quiz,
            code=code,
            defaults={**title.fields("title"), **description.fields("description")},
        )
        # Eski yozuvlarda izoh bo'lmasligi mumkin — bo'sh bo'lsa to'ldiramiz
        # (admin panelda yozilgan matn hech qachon qayta yozilmaydi).
        if not outcome.description_ru:
            outcome.description_ru = description.ru
            outcome.save(update_fields=["description_ru"])
        _fill_translations(outcome, title=title, description=description)
        outcomes[code] = outcome

    pairs = zip(QUESTIONS, QUESTION_SKILLS, strict=True)
    for order, ((text, options), skills) in enumerate(pairs, 1):
        question, question_created = Question.objects.get_or_create(
            quiz=quiz,
            text_ru=text.ru,
            defaults={**text.fields("text"), "order": order},
        )
        _fill_translations(question, text=text)

        if not question_created and question.options.exists():
            # Savol bor, variantlari ham bor — faqat tarjimalarni to'ldiramiz.
            existing = {option.text_ru: option for option in question.options.all()}
            for option_text, _code, _weight in options:
                option = existing.get(option_text.ru)
                if option is not None:
                    _fill_translations(option, text=option_text)
            continue

        for option_order, (option_text, code, weight) in enumerate(options, 1):
            Option.objects.get_or_create(
                question=question,
                text_ru=option_text.ru,
                defaults={
                    **option_text.fields("text"),
                    "outcome": outcomes[code],
                    "skill": skills[option_order - 1],
                    "weight": weight,
                    "order": option_order,
                },
            )

    return quiz
