import { L } from '@/i18n/localize'

import gallery1 from '@/assets/images/1_card.webp'
import gallery2 from '@/assets/images/2_card.webp'
import gallery3 from '@/assets/images/3_card.webp'

/**
 * «IT-разработка» sahifasi ma'lumotlari.
 *
 * Kontent maketda qat'iy belgilangan, shuning uchun admin paneldan emas,
 * shu fayldan olinadi — `itKids.js` bilan bir xil yondashuv.
 * Matnlar `L(uz, ru, en)` orqali uch tilda yoziladi.
 */

/** Hero ostidagi asosiy ko'rsatkichlar tasmasi. */
export const IT_DEV_FACTS = [
  {
    value: L('12–17 yosh', '12–17 лет', 'ages 12–17'),
    label: L('yosh', 'возраст', 'age'),
  },
  {
    value: L('24 oygacha', 'до 24 мес.', 'up to 24 mo.'),
    label: L('Davomiyligi', 'Продолжительность', 'Duration'),
  },
  {
    value: L('Loyihalar', 'Проекты', 'Projects'),
    label: L('Format', 'Формат', 'Format'),
  },
  {
    value: L('12 tagacha', 'до 12 уч.', 'up to 12'),
    label: L('Guruh', 'Группа', 'Group'),
  },
]

/** «Программы и инструменты» — `TECH` (directions.js) kalitlari. */
export const IT_DEV_TOOLS = ['html', 'css', 'js', 'react', 'python']

/** «О курсе» bo'limidagi aylanuvchi mavzu kartochkalari. */
export const IT_DEV_TOPICS = [
  {
    title: L('Saytlarni\nverstka qilish', 'Вёрстка\nсайтов', 'Website\nlayout'),
    description: L(
      'HTML va CSS: maketlar, moslashuvchanlik, animatsiyalar.',
      'HTML и CSS: макеты, адаптивность, анимации.',
      'HTML and CSS: layouts, responsiveness, animations.',
    ),
    icon: 'layers',
  },
  {
    title: L('JavaScript\nva interaktiv', 'JavaScript\nи интерактив', 'JavaScript\nand interaction'),
    description: L(
      'Brauzerdagi mantiq, DOM va API bilan ishlash.',
      'Логика в браузере, работа с DOM и API.',
      'Logic in the browser, working with the DOM and APIs.',
    ),
    icon: 'spark',
  },
  {
    title: L('Python\nva Telegram-botlar', 'Python\nи Telegram-боты', 'Python\nand Telegram bots'),
    description: L(
      'Birinchi backend va Telegram’dagi shaxsiy bot.',
      'Первый бэкенд и собственный бот в Telegram.',
      'A first backend and your own bot on Telegram.',
    ),
    icon: 'chat',
  },
  {
    title: L('Ma’lumotlar bazasi', 'Базы данных', 'Databases'),
    description: L(
      'Ma’lumot saqlash, SQL so‘rovlari, jadval bog‘lanishlari.',
      'Хранение данных, SQL-запросы, связи таблиц.',
      'Storing data, SQL queries, table relationships.',
    ),
    icon: 'cubes',
  },
  {
    title: L('Dasturlashda AI', 'ИИ в разработке', 'AI in development'),
    description: L(
      'AI-servislarni ulash va promptlar bilan ishlash.',
      'Подключение AI-сервисов и работа с промптами.',
      'Connecting AI services and working with prompts.',
    ),
    icon: 'brain',
  },
  {
    title: L('Git va jamoaviy\nish', 'Git и командная\nработа', 'Git and team\nwork'),
    description: L(
      'Repozitoriylar, branchlar, ko‘rib chiqish va birgalikdagi loyihalar.',
      'Репозитории, ветки, ревью и совместные проекты.',
      'Repositories, branches, reviews and shared projects.',
    ),
    icon: 'checklist',
  },
]

/** «Атмосфера занятий» galereyasi. */
export const IT_DEV_GALLERY = [
  {
    src: gallery1,
    alt: L(
      'O‘quv sinfidagi dasturlash darsi',
      'Занятие по программированию в учебном классе',
      'A programming lesson in the classroom',
    ),
  },
  {
    src: gallery2,
    alt: L(
      'Guruhda loyiha ustida ish',
      'Работа над проектом в группе',
      'Working on a project as a group',
    ),
  },
  {
    src: gallery3,
    alt: L(
      'Guruh oldida loyiha himoyasi',
      'Защита проекта перед группой',
      'Presenting a project to the group',
    ),
  },
]

/** «Три этапа обучения» — akkordeon bosqichlari. */
export const IT_DEV_STAGES = [
  {
    number: '01',
    title: L('Frontend: birinchi sayt', 'Frontend: первый сайт', 'Frontend: the first website'),
    duration: L('3 oy', '3 месяца', '3 months'),
    description: L(
      'O‘quvchi noldan sayt yig‘adi — belgilash va uslublardan tortib JavaScript’dagi interaktiv elementlargacha.',
      'Ученик с нуля собирает сайты — от разметки и стилей до интерактивных элементов на JavaScript.',
      'Students build websites from scratch — from markup and styles to interactive elements in JavaScript.',
    ),
    topics: L(
      [
        'HTML: sahifa strukturasi va semantika',
        'CSS: maketlar, Flexbox va moslashuvchanlik',
        'Animatsiyalar va zamonaviy verstka usullari',
        'JavaScript: o‘zgaruvchilar, shartlar, sikllar',
        'DOM va hodisalar bilan ishlash',
      ],
      [
        'HTML: структура страницы и семантика',
        'CSS: макеты, Flexbox и адаптивность',
        'Анимации и современные приёмы вёрстки',
        'JavaScript: переменные, условия, циклы',
        'Работа с DOM и событиями',
      ],
      [
        'HTML: page structure and semantics',
        'CSS: layouts, Flexbox and responsiveness',
        'Animations and modern layout techniques',
        'JavaScript: variables, conditionals, loops',
        'Working with the DOM and events',
      ],
    ),
    tools: ['html', 'css', 'js'],
    result: L(
      'SPACE platformasidagi o‘quvchi profilida chop etilgan shaxsiy moslashuvchan sayt.',
      'Собственный адаптивный сайт, опубликованный в профиле ученика на платформе SPACE.',
      'Their own responsive website, published on the student’s SPACE profile.',
    ),
  },
  {
    number: '02',
    title: L('Python va Telegram-botlar', 'Python и Telegram-боты', 'Python and Telegram bots'),
    duration: L('3 oy', '3 месяца', '3 months'),
    description: L(
      'Server tomoniga o‘tish: o‘quvchi Python’da yozadi va o‘z Telegram-botini ishga tushiradi.',
      'Переход к серверной части: ученик пишет на Python и запускает собственного Telegram-бота.',
      'Moving to the server side: students write Python and launch their own Telegram bot.',
    ),
    topics: L(
      [
        'Python sintaksisi va ma’lumot tuzilmalari',
        'Funksiyalar, modullar va xatolarni qayta ishlash',
        'Tashqi API’lar bilan ishlash',
        'Telegram Bot API: buyruqlar va stsenariylar',
        'Botni serverda chop etish va ishga tushirish',
      ],
      [
        'Синтаксис Python и структуры данных',
        'Функции, модули и обработка ошибок',
        'Работа с внешними API',
        'Telegram Bot API: команды и сценарии',
        'Публикация и запуск бота на сервере',
      ],
      [
        'Python syntax and data structures',
        'Functions, modules and error handling',
        'Working with external APIs',
        'Telegram Bot API: commands and flows',
        'Deploying and running a bot on a server',
      ],
    ),
    tools: ['python'],
    result: L(
      'Bir nechta buyruqqa ega va tushunarli dialog stsenariysi bo‘lgan ishlaydigan Telegram-bot.',
      'Работающий Telegram-бот с несколькими командами и понятным сценарием диалога.',
      'A working Telegram bot with several commands and a clear conversation flow.',
    ),
  },
  {
    number: '03',
    title: L(
      'Ma’lumotlar bazasi, React va AI',
      'Базы данных, React и ИИ',
      'Databases, React and AI',
    ),
    duration: L('3 oy', '3 месяца', '3 months'),
    description: L(
      'Yakuniy bosqich: ma’lumot saqlash, zamonaviy interfeys va AI funksiyalariga ega to‘laqonli servis.',
      'Финальный этап: полноценный сервис с хранением данных, современным интерфейсом и AI-функциями.',
      'The final stage: a complete service with data storage, a modern interface and AI features.',
    ),
    topics: L(
      [
        'Ma’lumotlar bazasi va SQL so‘rovlari',
        'Backend va ma’lumotlar bazasi bog‘lanishi',
        'React: komponentlar va holat',
        'Loyihaga AI-servislarni ulash',
        'Git, kodni ko‘rib chiqish va jamoaviy ish',
      ],
      [
        'Базы данных и SQL-запросы',
        'Связь бэкенда и базы данных',
        'React: компоненты и состояние',
        'Подключение AI-сервисов к проекту',
        'Git, ревью кода и командная работа',
      ],
      [
        'Databases and SQL queries',
        'Connecting the backend to the database',
        'React: components and state',
        'Adding AI services to the project',
        'Git, code review and teamwork',
      ],
    ),
    tools: ['react', 'python'],
    result: L(
      'Ma’lumotlar bazasiga ega yakuniy IT-loyiha va Demo Day’dagi taqdimot.',
      'Итоговый IT-проект с базой данных и презентация на Demo Day.',
      'A final IT project with a database and a presentation at Demo Day.',
    ),
  },
]

/** Bosqichlar bo'limining o'ng tomonidagi qisqa xulosa. */
export const IT_DEV_STAGES_SUMMARY = L(
  'Jami 9 oy · 3 bosqich',
  'Всего 9 месяцев · 3 этапа',
  '9 months in total · 3 stages',
)

/** Kurs bo'yicha tez-tez beriladigan savollar. */
export const IT_DEV_FAQ = [
  {
    id: 'base',
    question: L(
      'Boshlashdan oldin dasturlash bilimi kerakmi?',
      'Нужны ли знания программирования до старта?',
      'Is prior programming knowledge required?',
    ),
    answer: L(
      'Yo‘q. Kurs eng asosiy tushunchalardan boshlanadi — birinchi kod satrlarini o‘quvchi kirish darslaridayoq yozadi.',
      'Нет. Курс начинается с самых основ — первые строки кода ученик пишет уже на вводных занятиях.',
      'No. The course starts from the very basics — students write their first lines of code in the introductory lessons.',
    ),
  },
  {
    id: 'laptop',
    question: L(
      'O‘z noutbuki kerakmi?',
      'Нужен ли свой ноутбук?',
      'Does my child need their own laptop?',
    ),
    answer: L(
      'Yo‘q. Darslar jihozlangan sinflarda o‘tadi, barcha kompyuter va dasturlarni maktab beradi.',
      'Нет. Занятия проходят в оборудованных классах, все компьютеры и программы предоставляет школа.',
      'No. Classes take place in equipped classrooms; the school provides all computers and software.',
    ),
  },
  {
    id: 'missed',
    question: L(
      'Darsni o‘tkazib yuborsa nima bo‘ladi?',
      'Что будет, если пропустить занятие?',
      'What happens if a lesson is missed?',
    ),
    answer: L(
      'O‘qituvchi o‘tkazib yuborilgan mavzuni alohida tushuntiradi, materiallar va yozuv esa SPACE platformasidagi shaxsiy profilda qoladi.',
      'Преподаватель разберёт пропущенную тему индивидуально, а материалы и запись останутся в личном профиле ученика на платформе SPACE.',
      'The teacher goes through the missed topic one-on-one, and the materials and recording stay in the student’s profile on the SPACE platform.',
    ),
  },
]
