/**
 * Sayt bo'ylab yagona SEO manbasi.
 *
 * Bu fayl ikki joyda ishlatiladi:
 *  1. Ish vaqtida — `useSeo()` orqali sahifa meta-teglari va JSON-LD;
 *  2. Build vaqtida — `scripts/generate-seo.mjs` sitemap.xml, llms.txt va
 *     statik HTML (prerender) yasashda.
 *
 * Shuning uchun bu yerda faqat toza ma'lumot bo'ladi — brauzer API'lari yo'q,
 * Node ham shu faylni to'g'ridan-to'g'ri import qila oladi.
 *
 * Matnli maydonlar uch tilda beriladi: `L(uz, ru, en)`. Kerakli tilni
 * `resolvePage()` yoki `pick()` tanlaydi.
 */

/** Uch tilli qiymat. */
const L = (uz, ru, en) => ({ uz, ru, en })

/**
 * Sahifaning MA'LUM BIR TILDAGI manzili.
 *
 * Nega kerak: ilgari `hreflang="uz"`, `hreflang="ru"` va `hreflang="en"`
 * uchalasi BIR XIL manzilga ishora qilardi. Bu hreflang qoidasini buzadi —
 * har bir til alohida URL'da bo'lishi shart, aks holda Google belgini
 * butunlay e'tiborsiz qoldiradi va saytdan faqat bitta til indekslanadi.
 *
 * Til foydalanuvchi tomonida almashadi, shuning uchun eng kam qarshilikli
 * to'g'ri yechim — `?lang=` parametri. Asosiy til (uz) parametrsiz qoladi,
 * shunda mavjud havolalar va ulashilgan manzillar o'zgarmaydi.
 */
export function localeUrl(origin, path, locale) {
  const base = `${origin}${path === '/' ? '/' : path.replace(/\/$/, '')}`
  return locale === SITE.defaultLocale ? base : `${base}?lang=${locale}`
}

/** Sahifaning barcha til variantlari — `hreflang` va sitemap uchun. */
export function localeAlternates(origin, path) {
  return [
    ...SITE.locales.map((code) => ({ hreflang: code, href: localeUrl(origin, path, code) })),
    { hreflang: 'x-default', href: localeUrl(origin, path, SITE.defaultLocale) },
  ]
}

export const SITE = {
  name: 'MARS IT School',
  legalName: 'MARS IT School',
  /** Production manzili — `.env` dagi VITE_SITE_URL bundan ustun turadi. */
  url: 'https://marsitschool.uz',
  logo: '/logo-mars.png',
  ogImage: '/og-image.png',
  themeColor: '#0B0B0F',
  defaultLocale: 'uz',
  locales: ['uz', 'ru', 'en'],
  /** og:locale uchun to'liq kodlar. */
  ogLocales: { uz: 'uz_UZ', ru: 'ru_RU', en: 'en_US' },
  twitter: '@marsitschool',
  founded: '2019',
  geo: {
    country: 'UZ',
    countryName: L('O‘zbekiston', 'Узбекистан', 'Uzbekistan'),
    region: 'UZ-TK',
    city: L('Toshkent', 'Ташкент', 'Tashkent'),
    latitude: 41.311081,
    longitude: 69.240562,
    placename: 'Tashkent',
  },
  contacts: {
    phone: '+998 78 777 77 57',
    email: 'info@marsitschool.uz',
  },
  social: [
    'https://t.me/marsitschool',
    'https://www.instagram.com/marsitschool',
    'https://www.youtube.com/@marsitschool',
  ],
  /** Sayt tavsifi — llms.txt va tashkilot sxemasi uchun. */
  tagline: L(
    'Toshkentdagi 7–17 yoshli bolalar va o‘smirlar uchun dasturlash maktabi.',
    'Школа программирования для детей и подростков 7–17 лет в Ташкенте.',
    'A programming school for children and teenagers aged 7–17 in Tashkent.',
  ),
}

/**
 * Uch tilli qiymatdan kerakli tildagisini oladi. Oddiy satr bo'lsa —
 * o'zini qaytaradi, shuning uchun har qanday maydonda ishlatish mumkin.
 */
export function pick(value, locale = SITE.defaultLocale) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value[locale] ?? value[SITE.defaultLocale] ?? Object.values(value)[0]
  }
  return value
}

/**
 * Statik sahifalar. `path` — router yo'li, `priority`/`changefreq` — sitemap uchun.
 * `summary` — AEO/LLMO uchun qisqa, faktik javob (prerender va llms.txt'ga tushadi).
 */
export const STATIC_PAGES = [
  {
    path: '/',
    name: 'home',
    title: L(
      'Toshkentda bolalar uchun dasturlash maktabi',
      'Школа программирования для детей в Ташкенте',
      'Programming school for kids in Tashkent',
    ),
    heading: L(
      'MARS IT School — bolalar va o‘smirlar uchun dasturlash maktabi',
      'MARS IT School — школа программирования для детей и подростков',
      'MARS IT School — a programming school for kids and teens',
    ),
    description: L(
      'MARS IT School — Toshkentdagi 7–17 yoshli bolalar uchun dasturlash maktabi: saytlar, o‘yinlar, ilovalar va robototexnika. Kichik guruhlar, birinchi darsdan amaliyot, bepul sinov darsi.',
      'MARS IT School — школа программирования для детей 7–17 лет в Ташкенте: сайты, игры, приложения и робототехника. Малые группы, практика с первого занятия, бесплатный пробный урок.',
      'MARS IT School is a programming school for children aged 7–17 in Tashkent: websites, games, apps and robotics. Small groups, hands-on from day one, free trial lesson.',
    ),
    summary: L(
      'MARS IT School — Toshkentdagi 7–17 yoshli bolalar va o‘smirlar uchun dasturlash maktablari tarmog‘i. Yo‘nalishlar: IT Kids (9–11 yosh) va IT-dasturlash (12–17 yosh). Darslar 12 tagacha o‘quvchidan iborat kichik guruhlarda, haftasiga 2 marta, dastur davomiyligi 24 oygacha. Birinchi sinov darsi bepul.',
      'MARS IT School — сеть школ программирования для детей и подростков 7–17 лет в Ташкенте. Направления: IT Kids (9–11 лет) и IT-разработка (12–17 лет). Обучение проходит в малых группах до 12 учеников, занятия 2 раза в неделю, длительность программ до 24 месяцев. Первое пробное занятие бесплатное.',
      'MARS IT School is a network of programming schools for children and teenagers aged 7–17 in Tashkent. Tracks: IT Kids (ages 9–11) and IT Development (ages 12–17). Classes run in small groups of up to 12 students, twice a week, with programs lasting up to 24 months. The first trial lesson is free.',
    ),
    keywords: L(
      [
        'bolalar uchun dasturlash maktabi',
        'Toshkentda dasturlash kurslari',
        'bolalar uchun IT maktab',
        'o‘smirlar uchun dasturlash',
        'Toshkentda bolalar uchun robototexnika',
      ],
      [
        'школа программирования для детей',
        'курсы программирования Ташкент',
        'IT школа для детей',
        'программирование для подростков',
        'робототехника для детей Ташкент',
      ],
      [
        'programming school for kids',
        'coding courses Tashkent',
        'IT school for children',
        'programming for teenagers',
        'robotics for kids Tashkent',
      ],
    ),
    priority: 1.0,
    changefreq: 'weekly',
  },
  {
    path: '/o-nas',
    name: 'about',
    title: L('Biz haqimizda', 'О нас', 'About us'),
    heading: L(
      'MARS IT School maktabi haqida',
      'О школе MARS IT School',
      'About MARS IT School',
    ),
    description: L(
      'MARS IT School — Toshkentdagi bolalar va o‘smirlar uchun zamonaviy dasturlash maktabi: amaliyotchi o‘qituvchilar, mualliflik metodikasi va Demo Day’da loyihalar himoyasi.',
      'MARS IT School — современная школа программирования для детей и подростков в Ташкенте: преподаватели-практики, авторская методика и защита проектов на Demo Day.',
      'MARS IT School is a modern programming school for children and teens in Tashkent: working IT professionals as teachers, an in-house methodology and project defence at Demo Day.',
    ),
    summary: L(
      'MARS IT School 2019-yilda tashkil etilgan. O‘qituvchilar — amaliyotdagi IT mutaxassislari. Har bir modul o‘quvchining shaxsiy loyihasi bilan, kurs esa Demo Day’dagi ochiq himoya bilan yakunlanadi.',
      'MARS IT School основана в 2019 году. Преподаватели — практикующие IT-специалисты. Каждый модуль завершается собственным проектом ученика, а курс — публичной защитой на Demo Day.',
      'MARS IT School was founded in 2019. Its teachers are working IT professionals. Every module ends with the student’s own project, and every course ends with a public defence at Demo Day.',
    ),
    keywords: L(
      ['MARS IT School haqida', 'Toshkent IT maktabi sharhlari', 'dasturlash o‘qituvchilari'],
      ['о школе MARS IT School', 'IT школа Ташкент отзывы', 'преподаватели программирования'],
      ['about MARS IT School', 'IT school Tashkent reviews', 'programming teachers'],
    ),
    priority: 0.8,
    changefreq: 'monthly',
  },
  {
    path: '/kursy',
    name: 'courses',
    title: L(
      'Bolalar uchun dasturlash kurslari',
      'Курсы программирования для детей',
      'Programming courses for kids',
    ),
    heading: L('MARS IT School kurslari', 'Курсы MARS IT School', 'MARS IT School courses'),
    description: L(
      '7–17 yoshli bolalar va o‘smirlar uchun dasturlash va raqamli texnologiyalar kurslari: veb-dasturlash, Python, o‘yinlar, robototexnika va dizayn. Yoshga mos yo‘nalish tanlab beramiz.',
      'Курсы программирования и цифровых технологий для детей и подростков 7–17 лет: веб-разработка, Python, игры, робототехника и дизайн. Подберём направление по возрасту.',
      'Programming and digital technology courses for children and teens aged 7–17: web development, Python, games, robotics and design. We help pick a track by age.',
    ),
    summary: L(
      'MARS IT School kurslari ikki yo‘nalishga bo‘lingan: 9–11 yoshli bolalar uchun IT Kids va 12–17 yoshli o‘smirlar uchun IT-dasturlash. Ichida — veb-dasturlash (HTML, CSS, JavaScript), Python, o‘yin yaratish, robototexnika va raqamli dizayn.',
      'Каталог курсов MARS IT School разделён на два направления: IT Kids для детей 9–11 лет и IT-разработка для подростков 12–17 лет. Внутри — веб-разработка (HTML, CSS, JavaScript), Python, создание игр, робототехника и цифровой дизайн.',
      'The MARS IT School catalogue is split into two tracks: IT Kids for ages 9–11 and IT Development for ages 12–17. They cover web development (HTML, CSS, JavaScript), Python, game creation, robotics and digital design.',
    ),
    keywords: L(
      [
        'bolalar uchun dasturlash kurslari',
        'o‘smirlar uchun Python kurslari',
        'bolalar uchun veb-dasturlash',
        'Toshkentda robototexnika kurslari',
      ],
      [
        'курсы программирования для детей',
        'курсы Python для подростков',
        'веб-разработка для детей',
        'курсы робототехники Ташкент',
      ],
      [
        'coding courses for kids',
        'Python courses for teens',
        'web development for children',
        'robotics courses Tashkent',
      ],
    ),
    priority: 0.9,
    changefreq: 'weekly',
  },
  {
    path: '/kursy/it-kids',
    name: 'course-it-kids',
    title: L(
      'IT Kids — 9–11 yoshli bolalar uchun dasturlash',
      'IT Kids — программирование для детей 9–11 лет',
      'IT Kids — programming for ages 9–11',
    ),
    heading: L(
      'IT Kids — 9–11 yoshli bolalar uchun kurs',
      'IT Kids — курс для детей 9–11 лет',
      'IT Kids — a course for ages 9–11',
    ),
    description: L(
      'IT Kids — 9–11 yoshli bolalar uchun dasturlash va robototexnika kursi: birinchi darsdan amaliyot, 12 tagacha o‘quvchili guruhlar, 24 oygacha dastur.',
      'IT Kids — курс программирования и робототехники для детей 9–11 лет: практика с первого занятия, группы до 12 учеников, программа до 24 месяцев.',
      'IT Kids is a programming and robotics course for ages 9–11: hands-on from the first lesson, groups of up to 12 students, a program lasting up to 24 months.',
    ),
    summary: L(
      'IT Kids — 9–11 yoshli bolalar uchun kurs. Bolalar vizual va matnli dasturlashni, robototexnikani o‘zlashtiradi va o‘z o‘yinlarini yaratadi. Guruhlar 12 tagacha o‘quvchi, dastur davomiyligi 24 oygacha.',
      'IT Kids — курс для детей 9–11 лет. Дети осваивают визуальное и текстовое программирование, робототехнику и создают собственные игры. Группы до 12 учеников, длительность программы до 24 месяцев.',
      'IT Kids is a course for ages 9–11. Children learn visual and text-based programming and robotics, and build their own games. Groups of up to 12 students, programs lasting up to 24 months.',
    ),
    keywords: L(
      ['IT Kids', '9 yoshli bolalar uchun dasturlash', 'bolalar uchun robototexnika to‘garagi'],
      ['IT Kids', 'программирование для детей 9 лет', 'кружок робототехники для детей'],
      ['IT Kids', 'programming for 9 year olds', 'robotics club for children'],
    ),
    priority: 0.9,
    changefreq: 'monthly',
  },
  {
    path: '/kursy/it-razrabotka',
    name: 'course-it-razrabotka',
    title: L(
      'IT-dasturlash — 12–17 yoshli o‘smirlar uchun kurs',
      'IT-разработка — курс для подростков 12–17 лет',
      'IT Development — a course for ages 12–17',
    ),
    heading: L(
      'IT-dasturlash — 12–17 yoshli o‘smirlar uchun kurs',
      'IT-разработка — курс для подростков 12–17 лет',
      'IT Development — a course for ages 12–17',
    ),
    description: L(
      'IT-dasturlash — o‘smirlar uchun kompleks dastur: birinchi kod satrlaridan tortib o‘z saytlari, Telegram-botlari va ma’lumotlar bazasiga ega servislargacha.',
      'IT-разработка — комплексная программа для подростков: от первых строк кода до собственных сайтов, Telegram-ботов и сервисов с базами данных.',
      'IT Development is a complete program for teenagers: from the first lines of code to their own websites, Telegram bots and database-backed services.',
    ),
    summary: L(
      'IT-dasturlash — 12–17 yoshli o‘smirlar uchun dastur. O‘quvchilar HTML va CSS’dan JavaScript va Python’gacha yo‘lni bosib o‘tadi, saytlar, Telegram-botlar va ma’lumotlar bazasiga ega servislar yaratadi hamda loyihalar portfoliosini yig‘adi.',
      'IT-разработка — программа для подростков 12–17 лет. Ученики проходят путь от HTML и CSS до JavaScript и Python, создают сайты, Telegram-ботов и сервисы с базой данных, и собирают портфолио проектов.',
      'IT Development is a program for teenagers aged 12–17. Students move from HTML and CSS to JavaScript and Python, build websites, Telegram bots and database-backed services, and assemble a project portfolio.',
    ),
    keywords: L(
      ['o‘smirlar uchun IT kurslari', 'veb-dasturlashni o‘rganish', 'Toshkentda o‘smirlar uchun Python'],
      ['курсы IT для подростков', 'обучение веб-разработке', 'Python для подростков Ташкент'],
      ['IT courses for teens', 'learn web development', 'Python for teenagers Tashkent'],
    ),
    priority: 0.9,
    changefreq: 'monthly',
  },
  {
    path: '/space',
    name: 'space',
    title: L(
      'SPACE — o‘yinli o‘quv platformasi',
      'SPACE — игровая платформа обучения',
      'SPACE — a gamified learning platform',
    ),
    heading: L(
      'SPACE — o‘ynab o‘rgan',
      'SPACE — учись, играя',
      'SPACE — learn by playing',
    ),
    description: L(
      'SPACE — MARS IT School o‘yinli platformasi: topshiriqlar, dars yozuvlari, o‘zlashtirish va mukofotlar o‘quvchilar hamda ota-onalar uchun bitta ilovada.',
      'SPACE — игровая платформа MARS IT School: задания, записи занятий, успеваемость и награды в одном приложении для учеников и родителей.',
      'SPACE is the MARS IT School gamified platform: assignments, lesson recordings, progress and rewards in one app for students and parents.',
    ),
    summary: L(
      'SPACE — MARS IT School’ning o‘z platformasi. Unda o‘quvchi uy vazifalari, dars yozuvlari va o‘z taraqqiyotini ko‘radi, bajarilgan vazifalar uchun mukofot oladi, ota-onalar esa o‘zlashtirishni kuzatib boradi.',
      'SPACE — собственная платформа MARS IT School. В ней ученик видит домашние задания, записи занятий и прогресс, получает награды за выполненные задачи, а родители следят за успеваемостью.',
      'SPACE is the school’s own platform. Students see homework, lesson recordings and their progress, earn rewards for completed tasks, and parents follow along.',
    ),
    keywords: L(
      ['SPACE platformasi', 'onlayn dasturlashni o‘rganish', 'o‘qishni geymifikatsiya qilish'],
      ['платформа SPACE', 'обучение программированию онлайн', 'геймификация обучения'],
      ['SPACE platform', 'learn programming online', 'gamified learning'],
    ),
    priority: 0.7,
    changefreq: 'monthly',
  },
  {
    path: '/test',
    name: 'quiz',
    title: L(
      'Test: farzandingizga qaysi IT yo‘nalish mos keladi',
      'Тест: какое IT-направление подойдёт ребёнку',
      'Quiz: which IT track suits your child',
    ),
    heading: L(
      'Kasb tanlash testi',
      'Тест на профориентацию',
      'Career orientation quiz',
    ),
    description: L(
      'Qisqa testdan o‘ting va farzandingizga qaysi IT yo‘nalish mos kelishini biling — tavsiya etilgan kurs va o‘quv rejasi bilan.',
      'Пройдите короткий тест и узнайте, какое IT-направление подойдёт вашему ребёнку — с рекомендацией курса и плана обучения.',
      'Take a short quiz to find out which IT track suits your child — with a recommended course and learning plan.',
    ),
    summary: L(
      'Bir necha savoldan iborat bepul kasb tanlash testi. Natijaga ko‘ra ota-ona mos IT yo‘nalishni, tavsiya etilgan kursni va taxminiy o‘quv rejasini oladi.',
      'Бесплатный тест на профориентацию из нескольких вопросов. По результатам родитель получает подходящее IT-направление, рекомендуемый курс и примерный план обучения.',
      'A free career orientation quiz of a few questions. Parents get a matching IT track, a recommended course and an outline learning plan.',
    ),
    keywords: L(
      ['bolalar uchun kasb tanlash testi', 'qaysi IT yo‘nalishni tanlash'],
      ['тест на профориентацию для детей', 'какое IT направление выбрать'],
      ['career quiz for children', 'which IT track to choose'],
    ),
    priority: 0.6,
    changefreq: 'monthly',
  },
  {
    path: '/novosti',
    name: 'news',
    title: L(
      'Maktab yangiliklari va tadbirlari',
      'Новости и события школы',
      'School news and events',
    ),
    heading: L('MARS IT School yangiliklari', 'Новости MARS IT School', 'MARS IT School news'),
    description: L(
      'MARS IT School’da nimalar bo‘lyapti: tadbirlar, xakatonlar, o‘quvchilar loyihalari, Demo Day va yangi qabul e’lonlari.',
      'Что происходит в MARS IT School: события, хакатоны, проекты учеников, Demo Day и анонсы новых наборов.',
      'What is happening at MARS IT School: events, hackathons, student projects, Demo Day and new enrolment announcements.',
    ),
    summary: L(
      'MARS IT School yangiliklari bo‘limi: qabul e’lonlari, Demo Day va xakatonlar hisobotlari, o‘quvchilar loyihalari va maktab tadbirlari.',
      'Раздел новостей MARS IT School: анонсы наборов, отчёты с Demo Day и хакатонов, проекты учеников и события школы.',
      'The MARS IT School news section: enrolment announcements, Demo Day and hackathon reports, student projects and school events.',
    ),
    keywords: L(
      ['MARS IT School yangiliklari', 'Toshkent IT maktabi tadbirlari'],
      ['новости MARS IT School', 'события IT школы Ташкент'],
      ['MARS IT School news', 'IT school events Tashkent'],
    ),
    priority: 0.7,
    changefreq: 'daily',
  },
  {
    path: '/vakansii',
    name: 'vacancies',
    title: L('Vakansiyalar', 'Вакансии', 'Careers'),
    heading: L('MARS IT School vakansiyalari', 'Вакансии MARS IT School', 'Careers at MARS IT School'),
    description: L(
      'MARS IT School’ning Toshkentdagi ochiq vakansiyalari: dasturlash o‘qituvchilari, metodistlar va qo‘llab-quvvatlash jamoasi. Jamoamizga qo‘shiling.',
      'Открытые вакансии MARS IT School в Ташкенте: преподаватели программирования, методисты и команда поддержки. Присоединяйтесь к команде.',
      'Open roles at MARS IT School in Tashkent: programming teachers, curriculum designers and the support team. Join us.',
    ),
    summary: L(
      'MARS IT School Toshkentdagi filiallariga dasturlash o‘qituvchilari, metodistlar va qo‘llab-quvvatlash xodimlarini qabul qilmoqda. Ariza to‘g‘ridan-to‘g‘ri vakansiya sahifasida qoldiriladi.',
      'MARS IT School набирает преподавателей программирования, методистов и сотрудников поддержки в филиалы в Ташкенте. Отклик оставляется прямо на странице вакансии.',
      'MARS IT School is hiring programming teachers, curriculum designers and support staff for its Tashkent branches. Applications are submitted right on the vacancy page.',
    ),
    keywords: L(
      ['Toshkentda dasturlash o‘qituvchisi vakansiyasi', 'IT maktabida ish'],
      ['вакансии преподаватель программирования Ташкент', 'работа в IT школе'],
      ['programming teacher jobs Tashkent', 'work at an IT school'],
    ),
    priority: 0.5,
    changefreq: 'weekly',
  },
  {
    path: '/kontakty',
    name: 'contacts',
    title: L(
      'Kontaktlar va Toshkentdagi filiallar',
      'Контакты и филиалы в Ташкенте',
      'Contacts and branches in Tashkent',
    ),
    heading: L('MARS IT School kontaktlari', 'Контакты MARS IT School', 'MARS IT School contacts'),
    description: L(
      'MARS IT School’ning Toshkentdagi filiallari manzillari, telefonlari va xaritasi. Sizga eng yaqin filialga bepul sinov darsiga keling.',
      'Адреса филиалов MARS IT School в Ташкенте, телефоны и карта. Приходите на бесплатное пробное занятие в ближайший к вам филиал.',
      'Addresses, phone numbers and a map of MARS IT School branches in Tashkent. Come to your nearest branch for a free trial lesson.',
    ),
    summary: L(
      'MARS IT School Toshkentning bir necha filialida — Yunusobod, Chilonzor, Mirobod, Shayxontohur va Yashnobod tumanlarida ishlaydi. Sahifada manzillar, telefonlar va yo‘l xaritasi bor.',
      'MARS IT School работает в нескольких филиалах Ташкента — в Юнусабадском, Чиланзарском, Мирабадском, Шайхантахурском и Яшнабадском районах. На странице есть адреса, телефоны и карта проезда.',
      'MARS IT School operates several branches across Tashkent — in the Yunusabad, Chilanzar, Mirabad, Shaykhantakhur and Yashnabad districts. The page lists addresses, phone numbers and a map.',
    ),
    keywords: L(
      ['MARS IT School kontaktlari', 'Toshkent IT maktabi manzili', 'dasturlash maktabi filiallari'],
      ['MARS IT School контакты', 'IT школа Ташкент адрес', 'филиалы школы программирования'],
      ['MARS IT School contacts', 'IT school Tashkent address', 'programming school branches'],
    ),
    priority: 0.8,
    changefreq: 'monthly',
  },
  {
    path: '/zayavka',
    name: 'application',
    title: L(
      'Bepul sinov darsiga ariza',
      'Заявка на бесплатное пробное занятие',
      'Request a free trial lesson',
    ),
    heading: L('Ariza qoldirish', 'Оставить заявку', 'Leave a request'),
    description: L(
      'MARS IT School’da bepul sinov darsiga ariza qoldiring — o‘quv yo‘lini tanlashda yordam beramiz va barcha savollarga javob beramiz.',
      'Оставьте заявку на бесплатное пробное занятие в MARS IT School — поможем подобрать образовательный путь и ответим на все вопросы.',
      'Request a free trial lesson at MARS IT School — we will help choose a learning path and answer all your questions.',
    ),
    summary: L(
      'Bepul sinov darsiga yozilish shakli. Ariza qoldirilgach menejer ota-ona bilan bog‘lanadi, bolaning yoshiga mos yo‘nalishni tanlaydi va qulay vaqtni taklif qiladi.',
      'Форма записи на бесплатное пробное занятие. После заявки менеджер связывается с родителем, подбирает направление по возрасту ребёнка и предлагает удобное время.',
      'A form to book a free trial lesson. After the request a manager contacts the parent, picks a track matching the child’s age and offers a convenient time.',
    ),
    keywords: L(
      ['sinov darsiga yozilish', 'bepul dasturlash darsi'],
      ['записаться на пробное занятие', 'бесплатный урок программирования'],
      ['book a trial lesson', 'free programming lesson'],
    ),
    priority: 0.7,
    changefreq: 'monthly',
  },
]

/** Sahifadagi tarjima qilinadigan maydonlar. */
const LOCALIZED_FIELDS = ['title', 'heading', 'description', 'summary', 'keywords']

/** Uch tilli sahifani bitta tildagi oddiy obyektga aylantiradi. */
export function resolvePage(page, locale = SITE.defaultLocale) {
  if (!page) return page
  const resolved = { ...page }
  for (const field of LOCALIZED_FIELDS) {
    if (field in resolved) resolved[field] = pick(resolved[field], locale)
  }
  return resolved
}

/** Sitemap'ga tushmaydigan, indeksatsiyaga yopiq yo'llar. */
export const NOINDEX_PATTERNS = [/^\/test\/rezultat\//]

/** @returns {boolean} */
export function isNoindexPath(path) {
  return NOINDEX_PATTERNS.some((pattern) => pattern.test(path))
}

/** @returns {object|undefined} */
export function findStaticPage(path, locale = SITE.defaultLocale) {
  const page = STATIC_PAGES.find((item) => item.path === path)
  return page ? resolvePage(page, locale) : undefined
}
