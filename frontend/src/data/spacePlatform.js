/**
 * SPACE platformasining namoyish ma'lumotlari.
 *
 * Bu bo'lim — mahsulotning ko'rinishini ko'rsatuvchi maket (rasm emas, jonli
 * interfeys). Shu sababli kontent admin panelidan emas, shu fayldan olinadi.
 * Matnlar `L(uz, ru, en)` orqali uch tilda yoziladi.
 */
import { L } from '@/i18n/localize'

/** Texnologiya belgilari — rangli kvadrat ichidagi qisqartma. */
const TECH = {
  js: { label: 'JS', color: '#f7df1e', text: '#171717' },
  figma: { label: 'Fi', color: '#a259ff', text: '#ffffff' },
  react: { label: 'Re', color: '#61dafb', text: '#171717' },
  node: { label: 'No', color: '#3c873a', text: '#ffffff' },
  python: { label: 'Py', color: '#3776ab', text: '#ffffff' },
  git: { label: 'Gt', color: '#f05033', text: '#ffffff' },
}

/** Namoyishdagi sanalar — bir joyda, chunki bir necha ekranda takrorlanadi. */
const DATE = {
  may12: L('12-may', '12 мая', '12 May'),
  may15: L('15-may', '15 мая', '15 May'),
  may18: L('18-may', '18 мая', '18 May'),
  may20: L('20-may', '20 мая', '20 May'),
  may21: L('21-may', '21 мая', '21 May'),
  may25: L('25-may', '25 мая', '25 May'),
  may27: L('27-may', '27 мая', '27 May'),
  june1: L('1-iyun', '1 июня', '1 June'),
  yesterday: L('Kecha', 'Вчера', 'Yesterday'),
}

const STATUS = {
  inProgress: { label: L('Bajarilmoqda', 'В работе', 'In progress'), tone: 'brand' },
  onReview: { label: L('Tekshiruvda', 'На проверке', 'Under review'), tone: 'violet' },
  notStarted: { label: L('Boshlanmagan', 'Не начато', 'Not started'), tone: 'muted' },
  done: { label: L('Bajarildi', 'Выполнено', 'Completed'), tone: 'green' },
  newItem: { label: L('Yangi', 'Новое', 'New'), tone: 'brand' },
  watched: { label: L('Ko‘rilgan', 'Просмотрено', 'Watched'), tone: 'green' },
  watching: { label: L('Jarayonda', 'В процессе', 'In progress'), tone: 'violet' },
  good: { label: L('Yaxshi', 'Хорошо', 'Good'), tone: 'green' },
  excellent: { label: L('A’lo', 'Отлично', 'Excellent'), tone: 'green' },
  needsPractice: { label: L('Amaliyot kerak', 'Нужна практика', 'Needs practice'), tone: 'brand' },
  received: { label: L('Olingan', 'Получено', 'Earned'), tone: 'green' },
  available: { label: L('Mavjud', 'Доступно', 'Available'), tone: 'brand' },
  availableGreen: { label: L('Mavjud', 'Доступно', 'Available'), tone: 'green' },
  read: { label: L('O‘qilgan', 'Прочитано', 'Read'), tone: 'muted' },
  notEnough: {
    label: L('Ball yetmaydi', 'Не хватает баллов', 'Not enough points'),
    tone: 'brand',
  },
}

export const SPACE_MENU = [
  { id: 'homework', icon: 'book' },
  { id: 'lessons', icon: 'play' },
  { id: 'progress', icon: 'star' },
  { id: 'awards', icon: 'trophy' },
  { id: 'chat', icon: 'chat' },
  { id: 'shop', icon: 'bag' },
]

export const SPACE_VIEWS = {
  homework: {
    title: L('Uy vazifalari', 'Домашние задания', 'Homework'),
    subtitle: L(
      'Vazifalarni bajar va yangi bilimlar sari harakatlan',
      'Выполняй задания и двигайся к новым знаниям',
      'Complete assignments and move towards new knowledge',
    ),
    stats: [
      { value: '24', label: L('Jami vazifa', 'Всего заданий', 'Assignments total'), tone: 'brand' },
      { value: '6', label: L('Bajarilmoqda', 'В работе', 'In progress'), tone: 'violet' },
      { value: '16', label: L('Bajarildi', 'Выполнено', 'Completed'), tone: 'brand' },
      { value: '4.8', label: L('O‘rtacha baho', 'Средняя оценка', 'Average grade'), tone: 'amber' },
    ],
    tabs: L(
      ['Barcha vazifalar', 'Bajarilmoqda', 'Tekshiruvda', 'Bajarilganlari'],
      ['Все задания', 'В работе', 'На проверке', 'Выполненные'],
      ['All assignments', 'In progress', 'Under review', 'Completed'],
    ),
    rows: [
      {
        tech: TECH.js,
        title: L('JavaScript asoslari', 'Основы JavaScript', 'JavaScript basics'),
        subtitle: L(
          'Funksiyalar va ko‘rinish sohalari',
          'Функции и области видимости',
          'Functions and scope',
        ),
        status: STATUS.inProgress,
        meta: L('Muddat: {d}', 'Дедлайн: {d}', 'Due: {d}'),
        metaDate: DATE.may25,
        value: '60%',
      },
      {
        tech: TECH.figma,
        title: 'UI/UX Design',
        subtitle: L(
          'Bosh sahifa dizayni',
          'Дизайн главной страницы',
          'Home page design',
        ),
        status: STATUS.onReview,
        meta: L('Topshirildi: {d}', 'Сдано: {d}', 'Submitted: {d}'),
        metaDate: DATE.may20,
        value: '4.5 / 5',
      },
      {
        tech: TECH.react,
        title: L('Boshlovchilar uchun React', 'React для начинающих', 'React for beginners'),
        subtitle: L('Komponentlar va Props', 'Компоненты и Props', 'Components and props'),
        status: STATUS.inProgress,
        meta: L('Muddat: {d}', 'Дедлайн: {d}', 'Due: {d}'),
        metaDate: DATE.may27,
        value: '30%',
      },
      {
        tech: TECH.node,
        title: 'Node.js Backend',
        subtitle: L(
          'Ma’lumotlar bazasi bilan ishlash',
          'Работа с базой данных',
          'Working with a database',
        ),
        status: STATUS.notStarted,
        meta: L('Muddat: {d}', 'Дедлайн: {d}', 'Due: {d}'),
        metaDate: DATE.june1,
        value: '',
      },
      {
        tech: TECH.python,
        title: L(
          'Ma’lumot tahlili uchun Python',
          'Python для анализа данных',
          'Python for data analysis',
        ),
        subtitle: L('Pandas va vizualizatsiya', 'Pandas и визуализация', 'Pandas and charts'),
        status: STATUS.done,
        meta: L('Topshirildi: {d}', 'Сдано: {d}', 'Submitted: {d}'),
        metaDate: DATE.may15,
        value: '5 / 5',
      },
    ],
    aside: {
      type: 'calendar',
      title: L('Muddatlar kalendari', 'Календарь дедлайнов', 'Deadline calendar'),
    },
  },

  lessons: {
    title: L('Dars yozuvlari', 'Записи занятий', 'Lesson recordings'),
    subtitle: L(
      'Darsni o‘tkazib yubordingmi — yozuvni istalgan vaqtda ko‘r',
      'Пропустил урок — посмотри запись в любое время',
      'Missed a lesson? Watch the recording any time',
    ),
    stats: [
      { value: '48', label: L('Jami dars', 'Всего уроков', 'Lessons total'), tone: 'brand' },
      { value: '41', label: L('Ko‘rilgan', 'Просмотрено', 'Watched'), tone: 'green' },
      { value: '7', label: L('Yangi yozuvlar', 'Новые записи', 'New recordings'), tone: 'violet' },
      {
        value: L('12 s', '12ч', '12 h'),
        label: L('Ko‘rish vaqti', 'Время просмотра', 'Watch time'),
        tone: 'amber',
      },
    ],
    tabs: L(
      ['Barcha yozuvlar', 'Yangilari', 'Ko‘rilganlari'],
      ['Все записи', 'Новые', 'Просмотренные'],
      ['All recordings', 'New', 'Watched'],
    ),
    rows: [
      {
        tech: TECH.js,
        title: L(
          '12-dars. Massivlar va metodlar',
          'Урок 12. Массивы и методы',
          'Lesson 12. Arrays and methods',
        ),
        subtitle: L('JavaScript · 1 s 20 daq', 'JavaScript · 1 ч 20 мин', 'JavaScript · 1 h 20 min'),
        status: STATUS.newItem,
        meta: '{d}',
        metaDate: DATE.may21,
        value: '',
      },
      {
        tech: TECH.react,
        title: L(
          '11-dars. Komponent holati',
          'Урок 11. Состояние компонента',
          'Lesson 11. Component state',
        ),
        subtitle: L('React · 1 s 05 daq', 'React · 1 ч 05 мин', 'React · 1 h 05 min'),
        status: STATUS.watched,
        meta: '{d}',
        metaDate: DATE.may18,
        value: '100%',
      },
      {
        tech: TECH.figma,
        title: L(
          '10-dars. Setka va tipografika',
          'Урок 10. Сетка и типографика',
          'Lesson 10. Grid and typography',
        ),
        subtitle: L('UI/UX · 55 daq', 'UI/UX · 55 мин', 'UI/UX · 55 min'),
        status: STATUS.watched,
        meta: '{d}',
        metaDate: DATE.may15,
        value: '100%',
      },
      {
        tech: TECH.python,
        title: L(
          '9-dars. Ro‘yxat va lug‘atlar',
          'Урок 9. Списки и словари',
          'Lesson 9. Lists and dictionaries',
        ),
        subtitle: L('Python · 1 s 10 daq', 'Python · 1 ч 10 мин', 'Python · 1 h 10 min'),
        status: STATUS.watching,
        meta: '{d}',
        metaDate: DATE.may12,
        value: '45%',
      },
    ],
    aside: {
      type: 'progress',
      title: L('Haftalik faollik', 'Активность за неделю', 'Activity this week'),
    },
  },

  progress: {
    title: L('O‘zlashtirish', 'Успеваемость', 'Progress'),
    subtitle: L(
      'Taraqqiyotingni kuzat va yangi cho‘qqilarga chiq',
      'Отслеживай свой прогресс и достигай новых высот',
      'Track your progress and reach new heights',
    ),
    stats: [
      { value: '72%', label: L('Umumiy progress', 'Общий прогресс', 'Overall progress'), tone: 'brand' },
      { value: '24', label: L('Topshirilgan', 'Сдано заданий', 'Assignments handed in'), tone: 'violet' },
      { value: '6', label: L('Topshirilmagan', 'Не сдано', 'Not handed in'), tone: 'amber' },
      { value: '4.8', label: L('O‘rtacha baho', 'Средняя оценка', 'Average grade'), tone: 'green' },
    ],
    tabs: L(
      ['Barcha kurslar', 'Faol', 'Yakunlangan'],
      ['Все курсы', 'Активные', 'Завершённые'],
      ['All courses', 'Active', 'Completed'],
    ),
    rows: [
      {
        tech: TECH.js,
        title: L('JavaScript asoslari', 'Основы JavaScript', 'JavaScript basics'),
        subtitle: L(
          'Funksiyalar va ko‘rinish sohalari',
          'Функции и области видимости',
          'Functions and scope',
        ),
        status: STATUS.good,
        meta: L('Progress 75%', 'Прогресс 75%', 'Progress 75%'),
        value: '4.6',
      },
      {
        tech: TECH.react,
        title: L('React. Komponentlar va Props', 'React. Компоненты и Props', 'React. Components and props'),
        subtitle: L('Yakunlangan', 'Завершён', 'Completed'),
        status: STATUS.excellent,
        meta: L('Progress 100%', 'Прогресс 100%', 'Progress 100%'),
        value: '5.0',
      },
      {
        tech: TECH.node,
        title: 'Node.js Backend',
        subtitle: L(
          'Fayl tizimi bilan ishlash',
          'Работа с файловой системой',
          'Working with the file system',
        ),
        status: STATUS.needsPractice,
        meta: L('Progress 25%', 'Прогресс 25%', 'Progress 25%'),
        value: '3.2',
      },
      {
        tech: TECH.git,
        title: 'Git & GitHub',
        subtitle: L('Branchlar va Pull Requests', 'Ветки и Pull Requests', 'Branches and pull requests'),
        status: STATUS.good,
        meta: L('Progress 90%', 'Прогресс 90%', 'Progress 90%'),
        value: '4.4',
      },
    ],
    aside: {
      type: 'progress',
      title: L('O‘zlashtirish dinamikasi', 'Динамика успеваемости', 'Progress over time'),
    },
  },

  awards: {
    title: L('Ballar va mukofotlar', 'Баллы и награды', 'Points and rewards'),
    subtitle: L(
      'Vazifalar uchun ball to‘pla va ularni sovg‘aga almashtir',
      'Зарабатывай баллы за задания и обменивай их на призы',
      'Earn points for assignments and exchange them for prizes',
    ),
    stats: [
      { value: '2 450', label: L('Jami ball', 'Всего баллов', 'Points total'), tone: 'amber' },
      { value: '12', label: L('Daraja', 'Уровень', 'Level'), tone: 'brand' },
      { value: '9', label: L('Mukofot', 'Наград', 'Rewards'), tone: 'violet' },
      {
        value: '3',
        label: L('Yangi darajagacha', 'До нового уровня', 'To the next level'),
        tone: 'green',
      },
    ],
    tabs: L(
      ['Barcha mukofotlar', 'Olinganlari', 'Mavjudlari'],
      ['Все награды', 'Полученные', 'Доступные'],
      ['All rewards', 'Earned', 'Available'],
    ),
    rows: [
      {
        tech: TECH.js,
        title: L('Kod maratoni', 'Марафон кода', 'Code marathon'),
        subtitle: L(
          'Ketma-ket 7 kun tanaffussiz',
          '7 дней подряд без пропусков',
          '7 days in a row without a miss',
        ),
        status: STATUS.received,
        meta: L('+300 ball', '+300 баллов', '+300 points'),
        value: '',
      },
      {
        tech: TECH.figma,
        title: L('Hafta dizayneri', 'Дизайнер недели', 'Designer of the week'),
        subtitle: L('Guruhning eng yaxshi ishi', 'Лучшая работа группы', 'Best work in the group'),
        status: STATUS.received,
        meta: L('+250 ball', '+250 баллов', '+250 points'),
        value: '',
      },
      {
        tech: TECH.react,
        title: L('Birinchi loyiha', 'Первый проект', 'First project'),
        subtitle: L(
          'React’dagi shaxsiy ilova',
          'Собственное приложение на React',
          'Your own React application',
        ),
        status: STATUS.available,
        meta: L('+400 ball', '+400 баллов', '+400 points'),
        value: '',
      },
    ],
    aside: { type: 'progress', title: L('Daraja progressi', 'Прогресс уровня', 'Level progress') },
  },

  chat: {
    title: L('Muloqot', 'Общение', 'Chat'),
    subtitle: L(
      'O‘qituvchi va guruhdoshlar bilan chat',
      'Чат с преподавателем и одногруппниками',
      'Chat with your teacher and classmates',
    ),
    stats: [
      { value: '5', label: L('Faol chat', 'Активных чатов', 'Active chats'), tone: 'brand' },
      { value: '3', label: L('Yangi xabar', 'Новых сообщения', 'New messages'), tone: 'violet' },
      { value: '24', label: L('Guruhdosh', 'Одногруппников', 'Classmates'), tone: 'green' },
      { value: '2', label: L('O‘qituvchi', 'Преподавателя', 'Teachers'), tone: 'amber' },
    ],
    tabs: L(
      ['Barcha chatlar', 'Guruhlar', 'Shaxsiy'],
      ['Все чаты', 'Группы', 'Личные'],
      ['All chats', 'Groups', 'Direct'],
    ),
    rows: [
      {
        tech: TECH.js,
        title: L('JS-12 guruhi', 'Группа JS-12', 'Group JS-12'),
        subtitle: L(
          'Dilshod: muddatni unutmang',
          'Дилшод: не забудьте про дедлайн',
          'Dilshod: don’t forget the deadline',
        ),
        status: { label: L('3 ta yangi', '3 новых', '3 new'), tone: 'brand' },
        meta: '12:40',
        value: '',
      },
      {
        tech: TECH.figma,
        title: L('UI/UX klubi', 'UI/UX клуб', 'UI/UX club'),
        subtitle: L(
          'Malika: maket tahlilini joyladi',
          'Малика: выложила разбор макета',
          'Malika: posted a layout breakdown',
        ),
        status: STATUS.read,
        meta: '{d}',
        metaDate: DATE.yesterday,
        value: '',
      },
      {
        tech: TECH.react,
        title: L('Loyiha jamoasi', 'Проектная команда', 'Project team'),
        subtitle: L(
          'Timur: birinchi versiyani yig‘di',
          'Тимур: собрал первую версию',
          'Timur: put together the first version',
        ),
        status: { label: L('1 ta yangi', '1 новое', '1 new'), tone: 'brand' },
        meta: '{d}',
        metaDate: DATE.yesterday,
        value: '',
      },
    ],
    aside: {
      type: 'progress',
      title: L('Chatlardagi faollik', 'Активность в чатах', 'Chat activity'),
    },
  },

  shop: {
    title: 'MARS Shop',
    subtitle: L(
      'Topilgan ballarni sovg‘alarga almashtir',
      'Обменивай заработанные баллы на призы',
      'Exchange the points you earn for prizes',
    ),
    stats: [
      { value: '2 450', label: L('Sening balling', 'Твои баллы', 'Your points'), tone: 'amber' },
      { value: '18', label: L('Mahsulot', 'Товаров', 'Items'), tone: 'brand' },
      { value: '4', label: L('Senga mavjud', 'Доступно тебе', 'Available to you'), tone: 'green' },
      { value: '2', label: L('Savatda', 'В корзине', 'In the cart'), tone: 'violet' },
    ],
    tabs: L(
      ['Barcha mahsulotlar', 'Mavjudlari', 'Tez orada'],
      ['Все товары', 'Доступные', 'Скоро'],
      ['All items', 'Available', 'Coming soon'],
    ),
    rows: [
      {
        tech: TECH.git,
        title: L('MARS IT School xudisi', 'Худи MARS IT School', 'MARS IT School hoodie'),
        subtitle: L('S–XL o‘lchamlar', 'Размеры S–XL', 'Sizes S–XL'),
        status: STATUS.availableGreen,
        meta: L('2 000 ball', '2 000 баллов', '2,000 points'),
        value: '',
      },
      {
        tech: TECH.figma,
        title: L('Stikerlar to‘plami', 'Набор стикеров', 'Sticker pack'),
        subtitle: L('Mars bilan 12 ta stiker', '12 стикеров с Марсом', '12 Mars-themed stickers'),
        status: STATUS.availableGreen,
        meta: L('350 ball', '350 баллов', '350 points'),
        value: '',
      },
      {
        tech: TECH.react,
        title: L('Mexanik klaviatura', 'Механическая клавиатура', 'Mechanical keyboard'),
        subtitle: L('Oy sovrini', 'Приз месяца', 'Prize of the month'),
        status: STATUS.notEnough,
        meta: L('9 000 ball', '9 000 баллов', '9,000 points'),
        value: '',
      },
    ],
    aside: { type: 'progress', title: L('Ball to‘plash', 'Накопление баллов', 'Points earned') },
  },
}

/**
 * «Что умеет SPACE» bo'limi kartochkalari — maketda qat'iy belgilangan,
 * shuning uchun admin paneldan emas, shu fayldan olinadi.
 */
export const SPACE_FEATURES = [
  {
    id: 'courses',
    title: L('Mening kurslarim', 'Мои курсы', 'My courses'),
    description: L(
      'O‘quvchi kurs bo‘yicha taraqqiyotini ko‘radi: o‘tilgan modullar, darslar va bajarilish foizi. O‘qishni to‘xtagan joyidan davom ettirish mumkin.',
      'Ученик видит прогресс по курсу: пройденные модули, уроки и процент выполнения. Можно продолжить обучение с того места, где остановился.',
      'Students see their course progress: finished modules, lessons and completion percentage — and can pick up right where they left off.',
    ),
    icon: 'notes',
  },
  {
    id: 'eduverse',
    title: L('Eduverse', 'Эдуверс', 'Eduverse'),
    description: L(
      'Qo‘shimcha videokurslar kutubxonasi: HTML, CSS, Python, Blender, C#, C++ va Unity’da o‘yin yaratish — asosiy dasturdan tashqarida rivojlanish uchun.',
      'Библиотека дополнительных видеокурсов: HTML, CSS, Python, Blender, C#, создание игр на C++ и Unity — для развития вне основной программы.',
      'A library of extra video courses: HTML, CSS, Python, Blender, C#, and game development in C++ and Unity — for growth beyond the main program.',
    ),
    icon: 'book',
  },
  {
    id: 'marscode',
    title: 'MarsCode',
    description: L(
      'Yetakchi IT-kompaniyalar (Amazon, Google, Netflix, Facebook) uslubidagi amaliy masalalar — ko‘nikmalar haqiqiy keyslarda oshadi.',
      'Практические задачи в стиле топ-IT-компаний (Amazon, Google, Netflix, Facebook) — навыки прокачиваются на реальных кейсах.',
      'Practice problems in the style of top IT companies (Amazon, Google, Netflix, Facebook) — skills grow on real cases.',
    ),
    icon: 'code',
  },
  {
    id: 'blog',
    title: L('Blog', 'Блог', 'Blog'),
    description: L(
      'Ichki lenta: o‘quvchilar yutuqlari, natijalari va loyihalarini baham ko‘radi, muloqot qiladi va maktabning boshqa bolalaridan fikr oladi.',
      'Внутренняя лента: ученики делятся достижениями, результатами и проектами, общаются и получают отклик от других ребят школы.',
      'An internal feed: students share achievements, results and projects, talk to each other and get feedback from other students.',
    ),
    icon: 'feed',
  },
  {
    id: 'payment',
    title: L('Onlayn to‘lov', 'Оплата онлайн', 'Online payment'),
    description: L(
      'Ota-onalar va o‘quvchilar to‘g‘ridan-to‘g‘ri platformada to‘laydi, qarzdorlik tafsilotlari va to‘lovlar tarixini ko‘radi.',
      'Родители и ученики оплачивают обучение прямо на платформе, видят детали задолженности и историю платежей.',
      'Parents and students pay for tuition right on the platform and can see balance details and payment history.',
    ),
    icon: 'card',
  },
]

/** «Учиться — это увлекательно» bo'limidagi geymifikatsiya kartochkalari. */
export const SPACE_GAMIFICATION = [
  {
    id: 'coins',
    title: L('Ballar va koinlar', 'Баллы и коины', 'Points and coins'),
    description: L(
      'Darsdagi faollik, vazifalar va davomat uchun beriladi.',
      'Начисляются за активность на уроке, задания и посещаемость.',
      'Awarded for taking part in lessons, assignments and attendance.',
    ),
    icon: 'coins',
  },
  {
    id: 'streak',
    title: L('Kunlik strik', 'Ежедневный стрик', 'Daily streak'),
    description: L(
      'Platformada ketma-ket kunlar seriyasi — har kuni o‘qish odati.',
      'Серия дней подряд на платформе — привычка учиться каждый день.',
      'A run of consecutive days on the platform — the habit of learning daily.',
    ),
    icon: 'flame',
  },
  {
    id: 'rating',
    title: L('Umumiy reyting', 'Общий рейтинг', 'Overall ranking'),
    description: L(
      'O‘quvchilar orasidagi mavsumiy turnirlar va mavsum yakunidagi sovrinli o‘rinlar.',
      'Сезонные турниры между учениками и призовые места по итогам сезона.',
      'Seasonal tournaments between students, with prizes at the end of each season.',
    ),
    icon: 'trophy',
  },
  {
    id: 'games',
    title: L('Mini-o‘yinlar', 'Мини-игры', 'Mini-games'),
    description: L(
      'IT bo‘yicha o‘yin-mashqlar to‘g‘ridan-to‘g‘ri platformada — darslar orasida.',
      'Игровые тренажёры по IT прямо на платформе — между занятиями.',
      'Playful IT drills right on the platform — between lessons.',
    ),
    icon: 'gamepad',
  },
]

/** «Space Premium» bo'limidagi imkoniyatlar. */
export const SPACE_PREMIUM = [
  {
    id: 'coins',
    title: L('Davomat uchun 4 koin', '4 коина за посещаемость', '4 coins for attendance'),
    description: L(
      'Har bir qatnashgan dars uchun 2 barobar ko‘p koin.',
      'В 2 раза больше коинов за каждое посещённое занятие.',
      'Twice as many coins for every lesson attended.',
    ),
    icon: 'coins',
  },
  {
    id: 'marscode',
    title: L('Cheksiz MarsCode', 'Безлимитный MarsCode', 'Unlimited MarsCode'),
    description: L(
      'Masalalarni cheklovsiz yech va 60 tagacha koin ol.',
      'Решай задачи без ограничений и получай до 60 коинов.',
      'Solve problems without limits and earn up to 60 coins.',
    ),
    icon: 'code',
  },
  {
    id: 'eduverse',
    title: L('Cheksiz Eduverse', 'Безлимитный Eduverse', 'Unlimited Eduverse'),
    description: L(
      'Onlayn kurslarni o‘t va 80 tagacha koin ol.',
      'Проходи онлайн-курсы и получай до 80 коинов.',
      'Take online courses and earn up to 80 coins.',
    ),
    icon: 'book',
  },
  {
    id: 'marsiana',
    title: 'Marsiana',
    description: L(
      'Vazifalarni platformaning AI-yordamchisi bilan bajar.',
      'Выполняй задания с помощью AI-ассистента платформы.',
      'Work through assignments with the platform’s AI assistant.',
    ),
    icon: 'robot',
  },
  {
    id: 'badge',
    title: L('Premium nishoni', 'Значок Премиум', 'Premium badge'),
    description: L(
      'O‘quvchi ismi yonidagi eksklyuziv nishon.',
      'Эксклюзивный значок рядом с именем ученика.',
      'An exclusive badge next to the student’s name.',
    ),
    icon: 'badge',
  },
  {
    id: 'skins',
    title: L('Eksklyuziv skinlar', 'Эксклюзивные скины', 'Exclusive skins'),
    description: L(
      'Faqat Premium foydalanuvchilarga ochiq profil bezaklari.',
      'Оформление профиля, доступное только Премиум-пользователям.',
      'Profile themes available only to Premium users.',
    ),
    icon: 'palette',
  },
  {
    id: 'typing',
    title: L('Cheksiz SpaceTyping', 'Безлимитный SpaceTyping', 'Unlimited SpaceTyping'),
    description: L(
      'Matn terish tezligini oshirish uchun ko‘proq imkoniyat.',
      'Больше возможностей улучшить скорость набора текста.',
      'More ways to improve your typing speed.',
    ),
    icon: 'keyboard',
  },
  {
    id: 'blog',
    title: L('Cheksiz SpaceBlog', 'Безлимитный SpaceBlog', 'Unlimited SpaceBlog'),
    description: L(
      'Qiziqarli postlarni do‘stlaring bilan cheklovsiz baham ko‘r.',
      'Делись интересными постами с друзьями без ограничений.',
      'Share interesting posts with friends without limits.',
    ),
    icon: 'feed',
  },
]

/** «MARS Shop» bo'limidagi sovg'alar (narxi — koinlarda). */
export const SPACE_SHOP = [
  {
    id: 'alisa',
    title: L('Yandex Alisa aqlli kolonkasi', 'Умная колонка Яндекс Алиса', 'Yandex Alice smart speaker'),
    price: 2490,
    image: 'alisa',
  },
  {
    id: 'watch',
    title: L('Smart-soat', 'Смарт-часы', 'Smart watch'),
    price: 949,
    image: 'soat',
  },
  {
    id: 'headphones',
    title: L('Quloqchinlar', 'Наушники', 'Headphones'),
    price: 599,
    image: 'quloqchin',
  },
  {
    id: 'phone',
    title: L('Smartfonlar', 'Смартфоны', 'Smartphones'),
    price: 5400,
    image: 'smartfon',
  },
  {
    id: 'merch',
    title: L('Maktab merchi va aksessuarlari', 'Мерч и аксессуары школы', 'School merch and accessories'),
    price: 499,
    image: 'aksessuar',
  },
]

/**
 * «Родителям» bo'limidagi slaydlar.
 *
 * Har bir slayd ota-onaning ilovadagi bitta imkoniyatini ko'rsatadi.
 */
export const SPACE_PARENTS = [
  {
    id: 'attendance',
    title: L('Davomat', 'Посещаемость', 'Attendance'),
    description: L(
      'Darslar va qoldirilgan kunlar belgisi — administratorga qo‘ng‘iroq qilmasdan.',
      'Отметки о занятиях и пропусках — без звонков администратору.',
      'Lesson and absence records — without calling the administrator.',
    ),
  },
  {
    id: 'progress',
    title: L('O‘zlashtirish', 'Успеваемость', 'Progress'),
    description: L(
      'Modullar bo‘yicha baholar va bolaning o‘rtacha bali — oylar kesimida dinamikada.',
      'Оценки за модули и средний балл ребёнка — в динамике по месяцам.',
      'Module grades and the child’s average score — tracked month by month.',
    ),
  },
  {
    id: 'homework',
    title: L('Uy vazifalari', 'Домашние задания', 'Homework'),
    description: L(
      'Nima berilgani, nima topshirilgani va o‘qituvchi nimani tekshirgani ko‘rinadi.',
      'Видно, что задано, что сдано и что проверил преподаватель.',
      'You can see what was set, what was handed in and what the teacher has marked.',
    ),
  },
  {
    id: 'payment',
    title: L('O‘qish to‘lovi', 'Оплата обучения', 'Tuition payment'),
    description: L(
      'Kursni ilovadan onlayn to‘lash — kvitansiyalar va to‘lovlar tarixi ichida.',
      'Оплата курса онлайн из приложения — квитанции и история платежей внутри.',
      'Pay for the course online from the app — receipts and payment history included.',
    ),
  },
]
