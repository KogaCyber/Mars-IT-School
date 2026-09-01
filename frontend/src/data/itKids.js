import { L } from '@/i18n/localize'

import gallery1 from '@/assets/images/1_card.png'
import gallery2 from '@/assets/images/2_card.png'
import gallery3 from '@/assets/images/3_card.png'

/**
 * «IT Kids» sahifasi ma'lumotlari.
 *
 * Kontent maketda qat'iy belgilangan, shuning uchun admin paneldan emas,
 * shu fayldan olinadi — `directions.js` bilan bir xil yondashuv.
 * Matnlar `L(uz, ru, en)` orqali uch tilda yoziladi.
 */

/** Hero ostidagi asosiy ko'rsatkichlar tasmasi. */
export const IT_KIDS_FACTS = [
  {
    value: L('9–11 yosh', '9–11 лет', 'ages 9–11'),
    label: L('yosh', 'возраст', 'age'),
  },
  {
    value: L('24 oygacha', 'до 24 мес.', 'up to 24 mo.'),
    label: L('Davomiyligi', 'Продолжительность', 'Duration'),
  },
  {
    value: L('Amaliyot', 'Практика', 'Hands-on'),
    label: L('Format', 'Формат', 'Format'),
  },
  {
    value: L('12 tagacha', 'до 12 уч.', 'up to 12'),
    label: L('Guruh', 'Группа', 'Group'),
  },
]

/** «Программы и инструменты» — `TECH` (directions.js) kalitlari. */
export const IT_KIDS_TOOLS = ['html', 'css', 'js', 'react']

/** «О курсе» bo'limidagi aylanuvchi mavzu kartochkalari. */
export const IT_KIDS_TOPICS = [
  {
    title: L('Vizual\ndasturlash', 'Визуальное\nпрограммирование', 'Visual\nprogramming'),
    description: L(
      'Scratch: o‘yinlar, animatsiyalar, dastlabki algoritmlar.',
      'Scratch: игры, анимации, первые алгоритмы.',
      'Scratch: games, animations, first algorithms.',
    ),
    icon: 'blocks',
  },
  {
    title: L('Robototexnika', 'Робототехника', 'Robotics'),
    description: L(
      'Robot yig‘ish, datchiklar, motorlar, musobaqalar.',
      'Сборка роботов, датчики, моторы, соревнования.',
      'Building robots, sensors, motors, competitions.',
    ),
    icon: 'robot',
  },
  {
    title: L('Elektronika\nva Arduino', 'Электроника\nи Arduino', 'Electronics\nand Arduino'),
    description: L(
      'Aqlli uy, svetofor, signalizatsiya.',
      'Умный дом, светофор, сигнализация.',
      'Smart home, traffic lights, an alarm system.',
    ),
    icon: 'wrench',
  },
  {
    title: L('Dasturlash\nasoslari', 'Основы\nпрограммирования', 'Programming\nfundamentals'),
    description: L(
      'O‘zgaruvchilar, shartlar, sikllar — tushunarli misollarda.',
      'Переменные, условия, циклы на понятных примерах.',
      'Variables, conditionals and loops through clear examples.',
    ),
    icon: 'chip',
  },
  {
    title: L('Mantiq va algoritmlar', 'Логика и алгоритмы', 'Logic and algorithms'),
    description: L(
      'Masalani qadamlarga bo‘lish, xatolarni topish.',
      'Разбиение задачи на шаги, поиск ошибок.',
      'Breaking a task into steps and finding mistakes.',
    ),
    icon: 'brain',
  },
]

/** «Атмосфера занятий» galereyasi. */
export const IT_KIDS_GALLERY = [
  {
    src: gallery1,
    alt: L('O‘quv sinfidagi dars', 'Занятие в учебном классе', 'A lesson in the classroom'),
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
    alt: L('Darsda robot yig‘ish', 'Сборка робота на занятии', 'Assembling a robot in class'),
  },
]

/** «Три этапа обучения» — akkordeon bosqichlari. */
export const IT_KIDS_STAGES = [
  {
    number: '01',
    title: L(
      'IT va Scratch bilan tanishuv',
      'Знакомство с IT и Scratch',
      'Getting to know IT and Scratch',
    ),
    duration: L('3 oy', '3 месяца', '3 months'),
    description: L(
      'Bola kompyuterni o‘zlashtiradi va vizual dasturlash muhitida birinchi o‘yinlarini yaratadi.',
      'Ребёнок осваивает компьютер и создаёт первые игры в визуальной среде программирования.',
      'Children get comfortable with the computer and build their first games in a visual programming environment.',
    ),
    topics: L(
      [
        'Kompyuter tuzilishi va internetda xavfsiz ishlash',
        'Algoritmlar va ketma-ketliklar',
        'Scratch’da spraytlar, sahnalar va hodisalar',
        'O‘zgaruvchilar, shartlar va sikllar',
        'Birinchi o‘yin va animatsiya',
      ],
      [
        'Устройство компьютера и безопасная работа в интернете',
        'Алгоритмы и последовательности',
        'Спрайты, сцены и события в Scratch',
        'Переменные, условия и циклы',
        'Первая игра и анимация',
      ],
      [
        'How a computer works and staying safe online',
        'Algorithms and sequences',
        'Sprites, stages and events in Scratch',
        'Variables, conditionals and loops',
        'A first game and animation',
      ],
    ),
    tools: ['html', 'css', 'js'],
    result: L(
      'SPACE platformasidagi o‘quvchi profilida chop etilgan shaxsiy mini-o‘yin.',
      'Собственная мини-игра, опубликованная в профиле ученика на платформе SPACE.',
      'Their own mini-game, published on the student’s profile in the SPACE platform.',
    ),
  },
  {
    number: '02',
    title: L('Robototexnika', 'Робототехника', 'Robotics'),
    duration: L('3 oy', '3 месяца', '3 months'),
    description: L(
      'Ekrandan haqiqiy qurilmalarga o‘tish: robotlarni yig‘ish va dasturlash.',
      'Переход от экрана к реальным устройствам: сборка и программирование роботов.',
      'Moving from the screen to real devices: assembling and programming robots.',
    ),
    topics: L(
      [
        'Konstruksiyalar, motorlar va uzatmalar',
        'Masofa, yorug‘lik va tegish datchiklari',
        'Robotni blokli dasturlash',
        'Chiziq bo‘ylab harakat va to‘siqlarni aylanib o‘tish',
        'Jamoaviy musobaqalar',
      ],
      [
        'Конструкции, моторы и передачи',
        'Датчики расстояния, света и касания',
        'Блочное программирование робота',
        'Движение по линии и обход препятствий',
        'Командные соревнования',
      ],
      [
        'Structures, motors and gears',
        'Distance, light and touch sensors',
        'Block-based robot programming',
        'Line following and obstacle avoidance',
        'Team competitions',
      ],
    ),
    tools: ['cpp', 'python'],
    result: L(
      'Trassani bosib o‘tadigan va guruh oldida himoya qilinadigan yig‘ilgan robot.',
      'Собранный робот, который проходит трассу и защищается перед группой.',
      'An assembled robot that completes the course and is presented to the group.',
    ),
  },
  {
    number: '03',
    title: L(
      'Arduino va aqlli qurilmalar',
      'Arduino и умные устройства',
      'Arduino and smart devices',
    ),
    duration: L('3 oy', '3 месяца', '3 months'),
    description: L(
      'Bola elektron qurilmalar yig‘adi va ular uchun birinchi haqiqiy kodini yozadi.',
      'Ребёнок собирает электронные устройства и пишет для них первый настоящий код.',
      'Children assemble electronic devices and write their first real code for them.',
    ),
    topics: L(
      [
        'Elektr zanjirlari va maket plata',
        'Svetodiodlar, tugmalar va zummerlar',
        'Harorat, yorug‘lik va harakat datchiklari',
        'Arduino uchun C++’dagi birinchi kod',
        'Aqlli uy: svetofor va signalizatsiya',
      ],
      [
        'Электрические цепи и макетная плата',
        'Светодиоды, кнопки и зуммеры',
        'Датчики температуры, света и движения',
        'Первый код на C++ для Arduino',
        'Умный дом: светофор и сигнализация',
      ],
      [
        'Electric circuits and the breadboard',
        'LEDs, buttons and buzzers',
        'Temperature, light and motion sensors',
        'First C++ code for Arduino',
        'Smart home: traffic lights and an alarm',
      ],
    ),
    tools: ['cpp', 'python'],
    result: L(
      'Ishlaydigan aqlli qurilma va Demo Day’da loyiha taqdimoti.',
      'Работающее умное устройство и презентация проекта на Demo Day.',
      'A working smart device and a project presentation at Demo Day.',
    ),
  },
]

/** Bosqichlar bo'limining o'ng tomonidagi qisqa xulosa. */
export const IT_KIDS_STAGES_SUMMARY = L(
  'Jami 9 oy · 3 bosqich',
  'Всего 9 месяцев · 3 этапа',
  '9 months in total · 3 stages',
)

/** Kurs bo'yicha tez-tez beriladigan savollar. */
export const IT_KIDS_FAQ = [
  {
    id: 'age',
    question: L(
      'Necha yoshdan o‘qitasiz?',
      'С какого возраста обучение?',
      'From what age do you teach?',
    ),
    answer: L(
      'Bolalarni 7 yoshdan qabul qilamiz — dastur yoshga qarab tanlanadi.',
      'Мы принимаем детей с 7 лет — программа подбирается по возрасту.',
      'We accept children from age 7 — the program is chosen to match their age.',
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
      'Yo‘q. Barcha darslar jihozlangan sinflarda o‘tadi — kompyuter, robot va elektronika to‘plamlarini maktab beradi.',
      'Нет. Все занятия проходят в оборудованных классах — компьютеры, роботы и наборы электроники предоставляет школа.',
      'No. All classes take place in equipped classrooms — the school provides computers, robots and electronics kits.',
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
