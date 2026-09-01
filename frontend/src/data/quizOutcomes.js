/**
 * «Результаты теста» sahifasidagi tushuntirish matnlari.
 *
 * Test ikkita yo'nalishdan birini beradi (`outcome.code`): `backend` yoki
 * `frontend`. Har biri uchun sahifada bir xil tuzilma ko'rsatiladi:
 * ogohlantirish qatori, izoh, ikkita bosqich kartochkasi va yakuniy yorliqlar.
 *
 * Matnlar admin panelda emas, shu yerda — ular maketda qat'iy belgilangan va
 * yo'nalish nomlaridan boshqa o'zgaruvchisi yo'q. Uch til `L(uz, ru, en)`
 * orqali yonma-yon yoziladi.
 *
 * Har bir yo'nalishda ikkita blok bor:
 *   `label/headline/description/steps/chips` — sahifaning bosh qismi,
 *   `profile` — «Вашему ребёнку стоит начать с …» bo'limi.
 */
import { L } from '@/i18n/localize'

export const QUIZ_OUTCOME_DETAILS = {
  backend: {
    label: L('Muhim yo‘nalish', 'Важное направление', 'An important track'),
    headline: L(
      'Farzandingiz — Backend yo‘nalishida, ammo Frontend’dan boshlaydi!',
      'Ваш ребёнок — в направлении Backend, но начнёт с Frontend!',
      'Your child fits the Backend track — but should start with Frontend!',
    ),
    description: L(
      'Test natijalariga ko‘ra farzandingizda mantiqiy tafakkur, aniqlik va matematik fikrlash ustunlik qiladi — bu Backend uchun ideal. Ammo professional Backend-dasturchi bo‘lish uchun avval Frontend asoslarini o‘zlashtirish kerak!',
      'По результатам теста у вашего ребёнка преобладают логическое мышление, точность и математическое мышление — это идеально для Backend. Но чтобы стать профессиональным Backend-разработчиком, сначала нужно освоить основы Frontend!',
      'The test shows your child leads with logical thinking, precision and mathematical reasoning — ideal for Backend. But to become a professional Backend developer, they first need the Frontend fundamentals!',
    ),
    steps: [
      {
        number: '01',
        title: L(
          'Avval Frontend’ni o‘rganing',
          'Сначала изучите Frontend',
          'Start with Frontend',
        ),
        description: L(
          'HTML, CSS va JavaScript — hatto Backend-dasturchi uchun ham majburiy poydevor. Bu bilimlar API’ni sinashda va interfeys bilan bog‘lanishda doim kerak bo‘ladi.',
          'HTML, CSS и JavaScript — это обязательная основа даже для Backend-разработчика. Эти знания всегда нужны при тестировании API и связи с интерфейсом.',
          'HTML, CSS and JavaScript are a required foundation even for a Backend developer. You need them whenever you test an API or connect it to an interface.',
        ),
        tone: 'brand',
      },
      {
        number: '02',
        title: L(
          'Keyin Backend — oson bo‘ladi!',
          'Затем Backend — будет легко!',
          'Then Backend — it will feel easy!',
        ),
        description: L(
          'Frontend asoslarini biladigan bola Backend’ga o‘tganda 3 barobar tez o‘rganadi. Chunki u veb-texnologiyalarni tushunadi va mantiqiy bog‘lanishlarni ko‘radi.',
          'Ребёнок, знающий основы Frontend, при переходе к Backend учится в 3 раза быстрее. Потому что он понимает веб-технологии и видит логические связи.',
          'A child who knows Frontend basics learns Backend three times faster, because they already understand web technology and can see the logical connections.',
        ),
        tone: 'violet',
      },
    ],
    chips: [
      { label: L('1-bosqich', 'Этап 1', 'Stage 1'), value: 'HTML · CSS · JS' },
      { label: L('2-bosqich', 'Этап 2', 'Stage 2'), value: 'Python · SQL · API' },
      {
        label: L('Natija', 'Результат', 'Outcome'),
        value: L(
          'To‘laqonli Backend-dasturchi',
          'Полноценный Backend-разработчик',
          'A fully fledged Backend developer',
        ),
        accent: true,
      },
    ],

    profile: {
      eyebrow: L(
        'Backend Developer yo‘nalishi',
        'Направление Backend Developer',
        'Backend Developer track',
      ),
      title: L(
        ['Farzandingiz boshlashi kerak', 'BACKEND-dasturlashdan!'],
        ['Вашему ребёнку стоит начать', 'с BACKEND-разработки!'],
        ['Your child should start', 'with BACKEND development!'],
      ),
      intro: L(
        'Psixologik tahlil ko‘rsatishicha, farzandingizda MANTIQIY TAFAKKUR, MATEMATIK QOBILIYAT va ANIQLIKKA INTILISH ustunlik qiladi. Bular Backend-dasturchilarga kerak bo‘lgan eng qimmatli fazilatlar!',
        'Психологический анализ показывает, что у вашего ребёнка преобладают ЛОГИЧЕСКОЕ МЫШЛЕНИЕ, МАТЕМАТИЧЕСКИЕ СПОСОБНОСТИ и СТРЕМЛЕНИЕ К ТОЧНОСТИ. Это самые ценные качества, нужные Backend-разработчикам!',
        'The psychological analysis shows your child leads with LOGICAL THINKING, MATHEMATICAL ABILITY and A DRIVE FOR PRECISION. These are exactly the qualities Backend developers need!',
      ),
      points: [
        {
          text: L(
            'Murakkab masalalarni bosqichma-bosqich yechishni yoqtiradigan bolalar uchun ideal',
            'Идеально для детей, любящих решать сложные задачи шаг за шагом',
            'Ideal for children who enjoy solving complex problems step by step',
          ),
          icon: 'chart',
        },
        {
          text: L(
            'Matematik va mantiqiy tafakkur to‘liq qo‘llanadi — maktab matematikasi poydevorga aylanadi',
            'Полностью применяется математическое и логическое мышление — школьная математика становится основой',
            'Mathematical and logical thinking are fully used — school maths becomes the foundation',
          ),
          icon: 'logic',
        },
        {
          text: L(
            'Tizimlar va ma’lumotlar bilan ishlash — aniqlik va tartibni sevadiganlar uchun juda mos',
            'Работа с системами и данными — отлично подходит тем, кто любит точность и порядок',
            'Working with systems and data — a great fit for those who value precision and order',
          ),
          icon: 'code',
        },
        {
          text: L(
            'Oyiga 4 000–10 000 USD maosh — backend-dasturchilarga talab eng yuqori!',
            'Зарплата 4 000–10 000 USD в месяц — спрос на backend-разработчиков самый высокий!',
            'A salary of USD 4,000–10,000 a month — demand for backend developers is the highest!',
          ),
          icon: 'money',
        },
      ],

      note: {
        title: L(
          ['Ota-onalar uchun', 'muhim xabar:'],
          ['Важное сообщение', 'для родителей:'],
          ['An important message', 'for parents:'],
        ),
        text: L(
          'Farzandingizning tahliliy qobiliyati — texnologiya sohasidagi eng qimmatli resurs. Backend-dasturchi bo‘lish — kelajakning eng barqaror va yuqori haq to‘lanadigan kasblaridan biri!',
          'Аналитические способности вашего ребёнка — самый ценный ресурс в технологической индустрии. Стать backend-разработчиком — одна из самых стабильных и высокооплачиваемых профессий будущего!',
          'Your child’s analytical ability is the most valuable resource in the tech industry. Becoming a backend developer is one of the most stable and best-paid professions of the future!',
        ),
      },
    },

    path: {
      label: L(
        'Backend yo‘lidagi to‘g‘ri tartib',
        'Правильный порядок на пути Backend',
        'The right order on the Backend path',
      ),
      headline: L(
        'Avval Frontend → keyin Backend — professional yo‘l',
        'Сначала Frontend → потом Backend — профессиональный путь',
        'Frontend first → then Backend — the professional path',
      ),
      cards: [
        {
          number: '01',
          title: L('Avval Frontend’ni o‘rganing', 'Сначала изучите Frontend', 'Start with Frontend'),
          text: L(
            'HTML, CSS va JavaScript — hatto Backend-dasturchi uchun ham majburiy poydevor. Bu bilimlar API’ni sinashda va interfeys bilan bog‘lanishda doim kerak.',
            'HTML, CSS и JavaScript — обязательная основа даже для Backend-разработчика. Эти знания всегда нужны при тестировании API и связи с интерфейсом.',
            'HTML, CSS and JavaScript are a required foundation even for a Backend developer — needed whenever you test an API or wire it to an interface.',
          ),
        },
        {
          number: '02',
          title: L(
            'Backend’ga o‘ting — oson bo‘ladi! (4–6 oy)',
            'Переходите к Backend — будет легко! (4–6 месяцев)',
            'Move on to Backend — it will feel easy! (4–6 months)',
          ),
          text: L(
            'Python, Node.js, SQL va API — Frontend’ni biladigan bola bu bosqichni 2–3 barobar tez o‘zlashtiradi, chunki veb qanday ishlashini allaqachon tushunadi.',
            'Python, Node.js, SQL и API — ребёнок, знающий Frontend, осваивает этот этап в 2–3 раза быстрее, потому что уже понимает, как работает веб.',
            'Python, Node.js, SQL and APIs — a child who knows Frontend gets through this stage two to three times faster, because they already understand how the web works.',
          ),
        },
        {
          number: '03',
          title: L(
            'Professional Backend-dasturchi!',
            'Профессиональный Backend-разработчик!',
            'A professional Backend developer!',
          ),
          text: L(
            'Real loyihalar yaratadi, GitHub’da portfolio to‘playdi. Oyiga 4 000–10 000 USD topish imkoniyati.',
            'Создаёт реальные проекты, формирует портфолио на GitHub. Возможность зарабатывать 4 000–10 000 USD в месяц.',
            'They build real projects and grow a GitHub portfolio, with the potential to earn USD 4,000–10,000 a month.',
          ),
        },
        {
          number: '04',
          title: L(
            'MARS IT’da o‘qish qanday kechadi?',
            'Как проходит обучение в MARS IT?',
            'How does learning at MARS IT work?',
          ),
          text: L(
            'Backend yo‘nalishidagi barcha o‘quvchilar birinchi modulda Frontend asoslarini o‘tadi — bu majburiy shart. Tajribamiz ko‘rsatadi: to‘g‘ri tartibda o‘tgan bola eng yaxshi backend-dasturchilardan biriga aylanadi.',
            'Все ученики направления Backend проходят основы Frontend в первом модуле — это обязательное условие. Наш опыт показывает: ребёнок, прошедший правильный порядок, становится одним из лучших backend-разработчиков.',
            'Every student on the Backend track covers Frontend basics in the first module — that is a requirement. Our experience shows children who follow the right order become some of the strongest backend developers.',
          ),
        },
      ],
    },

    summaryNote: L(
      'Eslatma: Backend’ni o‘rganuvchi Frontend asoslarini ham egallashi kerak!',
      'Примечание: изучающему Backend нужно также освоить основы Frontend!',
      'Note: anyone learning Backend also needs the Frontend fundamentals!',
    ),

    plan: {
      label: L(
        'Backend’da start uchun reja',
        'План для старта в Backend',
        'A plan for starting in Backend',
      ),
      headline: L(
        'Backend yo‘lini boshlashga yordam beradigan bosqichma-bosqich marshrut.',
        'Пошаговый маршрут, который поможет начать путь в Backend.',
        'A step-by-step route to help start the Backend journey.',
      ),
      steps: [
        {
          number: '01',
          title: 'Python yoki Node.js',
          text: L(
            'Bu yerda mantiqiy tafakkur — asosiy kuch. Kod yozish va masala yechish ko‘nikmasi rivojlanadi.',
            'Логическое мышление — главная сила здесь. Развивается умение писать код и решать задачи.',
            'Logical thinking is the main strength here. Coding and problem-solving skills grow.',
          ),
        },
        {
          number: '02',
          title: L('Ma’lumotlar bazasi (SQL)', 'База данных (SQL)', 'Databases (SQL)'),
          text: L(
            'Millionlab yozuvni boshqarish — aniqlik va tartibga intilish uchun ideal soha.',
            'Управление миллионами записей — идеальная сфера для тяги к точности и порядку.',
            'Managing millions of records — a perfect fit for a love of precision and order.',
          ),
        },
        {
          number: '03',
          title: L('API va server mantig‘i', 'API и серверная логика', 'APIs and server logic'),
          text: L(
            'Ilovalarning ichki qismi — boshqalar ko‘rmaydigan, ammo hammasini ishlatadigan narsa.',
            'Внутренняя часть приложений — то, что не видят другие, но что заставляет всё работать.',
            'The inner half of an application — invisible to others, yet what makes everything work.',
          ),
        },
        {
          number: '04',
          title: L('Real loyiha va GitHub', 'Реальный проект и GitHub', 'A real project and GitHub'),
          text: L(
            'Telegram-bot, veb-server yoki AI-ilova — ish beruvchilar aynan shuni ko‘radi.',
            'Telegram-бот, веб-сервер или AI-приложение — именно это смотрят работодатели.',
            'A Telegram bot, a web server or an AI app — exactly what employers look at.',
          ),
        },
      ],
    },
  },

  frontend: {
    label: L('Muhim yo‘nalish', 'Важное направление', 'An important track'),
    headline: L(
      'Farzandingiz — Frontend yo‘nalishida!',
      'Ваш ребёнок — в направлении Frontend!',
      'Your child fits the Frontend track!',
    ),
    description: L(
      'Test natijalariga ko‘ra farzandingizda obrazli tafakkur, tafsilotlarga e’tibor va uslub tuyg‘usi ustunlik qiladi — bu Frontend uchun ideal. Verstka asoslaridan boshlab, so‘ng zamonaviy dasturlash vositalariga o‘tish kerak.',
      'По результатам теста у вашего ребёнка преобладают образное мышление, внимание к деталям и чувство стиля — это идеально для Frontend. Начать стоит с основ вёрстки, а затем перейти к современным инструментам разработки.',
      'The test shows your child leads with visual thinking, attention to detail and a sense of style — ideal for Frontend. Start with layout fundamentals, then move on to modern development tools.',
    ),
    steps: [
      {
        number: '01',
        title: L(
          'Frontend asoslaridan boshlang',
          'Начните с основ Frontend',
          'Start with the Frontend basics',
        ),
        description: L(
          'HTML, CSS va JavaScript — har qanday interfeysning poydevori. Birinchi darslardanoq bola o‘z ishining natijasini ekranda ko‘radi.',
          'HTML, CSS и JavaScript — фундамент любого интерфейса. С первых занятий ребёнок видит результат своей работы прямо на экране.',
          'HTML, CSS and JavaScript are the foundation of any interface. From the first lessons children see the result of their work right on screen.',
        ),
        tone: 'brand',
      },
      {
        number: '02',
        title: L('Keyin — real loyihalar', 'Затем — реальные проекты', 'Then — real projects'),
        description: L(
          'React, API bilan ishlash va Git verstkani to‘laqonli ilovalarga aylantiradi. O‘qish oxirida bolada o‘z loyihalari portfoliosi bo‘ladi.',
          'React, работа с API и Git превращают вёрстку в полноценные приложения. К концу обучения у ребёнка есть портфолио собственных проектов.',
          'React, APIs and Git turn markup into full applications. By the end of the course your child has a portfolio of their own projects.',
        ),
        tone: 'violet',
      },
    ],
    chips: [
      { label: L('1-bosqich', 'Этап 1', 'Stage 1'), value: 'HTML · CSS · JS' },
      { label: L('2-bosqich', 'Этап 2', 'Stage 2'), value: 'React · Git · API' },
      {
        label: L('Natija', 'Результат', 'Outcome'),
        value: L(
          'To‘laqonli Frontend-dasturchi',
          'Полноценный Frontend-разработчик',
          'A fully fledged Frontend developer',
        ),
        accent: true,
      },
    ],

    profile: {
      eyebrow: L(
        'Frontend Developer yo‘nalishi',
        'Направление Frontend Developer',
        'Frontend Developer track',
      ),
      title: L(
        ['Farzandingiz boshlashi kerak', 'FRONTEND-dasturlashdan!'],
        ['Вашему ребёнку стоит начать', 'с FRONTEND-разработки!'],
        ['Your child should start', 'with FRONTEND development!'],
      ),
      intro: L(
        'Psixologik tahlil ko‘rsatishicha, farzandingizda OBRAZLI TAFAKKUR, TAFSILOTLARGA E’TIBOR va USLUB TUYG‘USI ustunlik qiladi. Bular Frontend-dasturchilarga kerak bo‘lgan eng qimmatli fazilatlar!',
        'Психологический анализ показывает, что у вашего ребёнка преобладают ОБРАЗНОЕ МЫШЛЕНИЕ, ВНИМАНИЕ К ДЕТАЛЯМ и ЧУВСТВО СТИЛЯ. Это самые ценные качества, нужные Frontend-разработчикам!',
        'The psychological analysis shows your child leads with VISUAL THINKING, ATTENTION TO DETAIL and A SENSE OF STYLE. These are exactly the qualities Frontend developers need!',
      ),
      points: [
        {
          text: L(
            'O‘z ishining natijasini darrov ekranda ko‘rishni istaydigan bolalar uchun ideal',
            'Идеально для детей, которые хотят видеть результат своей работы сразу на экране',
            'Ideal for children who want to see the result of their work immediately on screen',
          ),
          icon: 'chart',
        },
        {
          text: L(
            'Vizual tafakkur to‘liq ochiladi — did va ozodalik kasbga aylanadi',
            'Полностью раскрывается визуальное мышление — вкус и аккуратность становятся профессией',
            'Visual thinking is fully unlocked — taste and tidiness turn into a profession',
          ),
          icon: 'logic',
        },
        {
          text: L(
            'Interfeys va animatsiya bilan ishlash — qulay va chiroyli qilishni yoqtiradiganlar uchun juda mos',
            'Работа с интерфейсами и анимацией — отлично подходит тем, кто любит делать удобно и красиво',
            'Working with interfaces and animation — a great fit for those who like making things usable and beautiful',
          ),
          icon: 'code',
        },
        {
          text: L(
            'Oyiga 3 000–8 000 USD maosh — frontend-dasturchilar har bir mahsulotga kerak!',
            'Зарплата 3 000–8 000 USD в месяц — frontend-разработчики нужны каждому продукту!',
            'A salary of USD 3,000–8,000 a month — every product needs frontend developers!',
          ),
          icon: 'money',
        },
      ],

      note: {
        title: L(
          ['Ota-onalar uchun', 'muhim xabar:'],
          ['Важное сообщение', 'для родителей:'],
          ['An important message', 'for parents:'],
        ),
        text: L(
          'Tushunarli va chiroyli interfeys yarata olish — har qanday texnologiya kompaniyasida qadrlanadigan ko‘nikma. Frontend-dasturlash — kelajakning eng talab yuqori va ijodiy kasblaridan biri!',
          'Умение делать понятные и красивые интерфейсы — навык, который ценится в любой технологической компании. Frontend-разработка — одна из самых востребованных и творческих профессий будущего!',
          'Being able to build clear, beautiful interfaces is valued at any technology company. Frontend development is one of the most in-demand and creative professions of the future!',
        ),
      },
    },

    path: {
      label: L(
        'Frontend yo‘lidagi to‘g‘ri tartib',
        'Правильный порядок на пути Frontend',
        'The right order on the Frontend path',
      ),
      headline: L(
        'Asoslar → freymvorklar → real loyihalar — professional yo‘l',
        'Основы → фреймворки → реальные проекты — профессиональный путь',
        'Fundamentals → frameworks → real projects — the professional path',
      ),
      cards: [
        {
          number: '01',
          title: L('Verstkadan boshlang', 'Начните с вёрстки', 'Start with layout'),
          text: L(
            'HTML va CSS — har qanday interfeysning asosi. Birinchi darslardayoq bola telefonda ham, kompyuterda ham to‘g‘ri ko‘rinadigan sahifalar yig‘adi.',
            'HTML и CSS — основа любого интерфейса. Уже на первых занятиях ребёнок собирает страницы, которые корректно выглядят на телефоне и компьютере.',
            'HTML and CSS are the base of any interface. From the very first lessons children build pages that look right on both phone and desktop.',
          ),
        },
        {
          number: '02',
          title: L(
            'JavaScript qo‘shing (3–4 oy)',
            'Добавьте JavaScript (3–4 месяца)',
            'Add JavaScript (3–4 months)',
          ),
          text: L(
            'Mantiq, hodisalar va ma’lumotlar bilan ishlash sahifani jonlantiradi. Bu yerda bola birinchi marta haqiqiy kod yozadi va natijani darrov ekranda ko‘radi.',
            'Логика, события и работа с данными оживляют страницу. Здесь ребёнок впервые пишет настоящий код и видит результат сразу на экране.',
            'Logic, events and data bring the page to life. Here children write real code for the first time and see the result instantly.',
          ),
        },
        {
          number: '03',
          title: L(
            'Professional Frontend-dasturchi!',
            'Профессиональный Frontend-разработчик!',
            'A professional Frontend developer!',
          ),
          text: L(
            'React, Git va API bilan ishlash verstkani ilovalarga aylantiradi. GitHub’da portfolio va oyiga 3 000–8 000 USD topish imkoniyati.',
            'React, Git и работа с API превращают вёрстку в приложения. Портфолио на GitHub и возможность зарабатывать 3 000–8 000 USD в месяц.',
            'React, Git and APIs turn markup into applications. A GitHub portfolio and the potential to earn USD 3,000–8,000 a month.',
          ),
        },
        {
          number: '04',
          title: L(
            'MARS IT’da o‘qish qanday kechadi?',
            'Как проходит обучение в MARS IT?',
            'How does learning at MARS IT work?',
          ),
          text: L(
            'Har bir modul shaxsiy loyiha va guruh oldida himoya bilan yakunlanadi. Bola nafaqat kod yozishni, balki o‘z qarorlarini tushuntirishni ham o‘rganadi.',
            'Каждый модуль заканчивается собственным проектом и защитой перед группой. Ребёнок учится не только писать код, но и объяснять свои решения.',
            'Every module ends with the student’s own project and a presentation to the group. Children learn not only to write code, but to explain their decisions.',
          ),
        },
      ],
    },

    summaryNote: L(
      'Eslatma: Frontend asoslaridan keyin Backend’ga o‘tish oson kechadi — bu fullstack-dasturlash sari yo‘l!',
      'Примечание: после основ Frontend переход к Backend даётся легко — это путь к fullstack-разработке!',
      'Note: after the Frontend fundamentals, moving to Backend is easy — it is the path to fullstack development!',
    ),

    plan: {
      label: L(
        'Frontend’da start uchun reja',
        'План для старта в Frontend',
        'A plan for starting in Frontend',
      ),
      headline: L(
        'Frontend yo‘lini boshlashga yordam beradigan bosqichma-bosqich marshrut.',
        'Пошаговый маршрут, который поможет начать путь в Frontend.',
        'A step-by-step route to help start the Frontend journey.',
      ),
      steps: [
        {
          number: '01',
          title: 'HTML & CSS',
          text: L(
            'Sahifa verstkasi, setkalar va moslashuvchanlik — har qanday interfeys tayanadigan poydevor.',
            'Вёрстка страниц, сетки и адаптивность — фундамент, на котором держится любой интерфейс.',
            'Page layout, grids and responsiveness — the foundation every interface rests on.',
          ),
        },
        {
          number: '02',
          title: 'JavaScript',
          text: L(
            'Mantiq, hodisalar va ma’lumotlar bilan ishlash — sahifa jonlanadi va foydalanuvchiga javob bera boshlaydi.',
            'Логика, события и работа с данными — страница оживает и начинает отвечать пользователю.',
            'Logic, events and data — the page comes alive and starts responding to the user.',
          ),
        },
        {
          number: '03',
          title: L('React va API bilan ishlash', 'React и работа с API', 'React and APIs'),
          text: L(
            'Komponentlar, holat va serverdan kelgan ma’lumotlar — zamonaviy ilovalar shunday yig‘iladi.',
            'Компоненты, состояние и данные с сервера — так собираются современные приложения.',
            'Components, state and server data — this is how modern applications are put together.',
          ),
        },
        {
          number: '04',
          title: L('Real loyiha va GitHub', 'Реальный проект и GitHub', 'A real project and GitHub'),
          text: L(
            'Portfoliodagi shaxsiy sayt yoki veb-ilova — ish beruvchilar aynan shuni ko‘radi.',
            'Собственный сайт или веб-приложение в портфолио — именно это смотрят работодатели.',
            'Your own website or web app in the portfolio — exactly what employers look at.',
          ),
        },
      ],
    },
  },
}

/**
 * Yo'nalishlarning texnologiya to'plami — «Совпадение» kartochkalaridagi
 * yorliqlar. Ikonkasi yo'q texnologiyalar nuqta bilan ko'rsatiladi.
 */
export const DIRECTION_STACKS = {
  frontend: [
    { label: 'HTML', icon: 'html' },
    { label: 'CSS', icon: 'css' },
    { label: 'JavaScript', icon: 'js' },
    { label: 'React', icon: 'react' },
  ],
  backend: [
    { label: 'Python', icon: 'python' },
    { label: 'SQL' },
    { label: 'API' },
    { label: 'Node.js' },
  ],
}

/**
 * Ko'nikmalarning izohi — natija sahifasida foydalanuvchining eng kuchli
 * tomonlari shu matnlar bilan tushuntiriladi.
 */
export const SKILL_STRENGTHS = {
  logic: L(
    'Bola masalani qismlarga ajratadi va yechimni oxiriga yetkazadi — algoritmlar va server mantig‘i uchun poydevor.',
    'Ребёнок разбирает задачу на части и доводит решение до конца — основа для алгоритмов и серверной логики.',
    'The child breaks a task into parts and sees the solution through — the basis for algorithms and server logic.',
  ),
  math: L(
    'Sonlar va qonuniyatlar oson beriladi — bu algoritmlarni o‘zlashtirish va ma’lumot bilan ishlashni tezlashtiradi.',
    'Числа и закономерности даются легко — это ускоряет освоение алгоритмов и работу с данными.',
    'Numbers and patterns come easily — this speeds up learning algorithms and working with data.',
  ),
  accuracy: L(
    'Aniqlik va tartibga e’tibor — ma’lumotlar bazasi va testlashda ajralmas fazilat.',
    'Внимание к точности и порядку — качество, без которого не обойтись в базах данных и тестировании.',
    'Attention to precision and order — indispensable in databases and testing.',
  ),
  patience: L(
    'Bitta masala ustida uzoq ishlay olish — dasturlashda katta yordam beradigan kamyob fazilat.',
    'Умение долго работать над одной задачей — редкое качество, которое сильно помогает в разработке.',
    'The ability to stay with one problem for a long time — a rare quality that helps a lot in development.',
  ),
  creativity: L(
    'Bola yangi narsa o‘ylab topadi va sinab ko‘radi — bu interfeys dizayni va nostandart yechimlarda ko‘rinadi.',
    'Ребёнок придумывает и пробует новое — это видно в дизайне интерфейсов и нестандартных решениях.',
    'The child invents and tries new things — visible in interface design and unconventional solutions.',
  ),
  visual: L(
    'Rivojlangan vizual idrok: bola bezak tafsilotlari va ekran kompozitsiyasini payqaydi.',
    'Развитое визуальное восприятие: ребёнок замечает детали оформления и композицию экрана.',
    'Strong visual perception: the child notices styling details and the composition of a screen.',
  ),
  communication: L(
    'Fikrini oson tushuntiradi — bu jamoaviy ish va loyiha himoyasida yordam beradi.',
    'Легко объясняет свои мысли — это помогает в командной работе и защите проектов.',
    'Explains their thinking easily — this helps in teamwork and defending projects.',
  ),
  social: L(
    'Bola guruhda o‘zini qulay his qiladi — birgalikdagi loyihalar va jamoa ishi oson kechadi.',
    'Ребёнку комфортно в группе — совместные проекты и работа в команде будут даваться легко.',
    'The child is comfortable in a group — joint projects and teamwork will come easily.',
  ),
}
