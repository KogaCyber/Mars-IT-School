/**
 * Sayt ma'lumotlaridan yig'iladigan javob shablonlari.
 *
 * Statik javoblar `assistantFaq.js` da, bu yerda esa raqam va ro'yxat
 * qo'yiladigan gaplar turadi: `{count}`, `{names}`, `{list}`, `{phone}` …
 * O'rinlarni `utils/assistant.js` to'ldiradi.
 */
import { L } from '@/i18n/localize'

export const REPLIES = {
  /* --- Filiallar --------------------------------------------------------- */
  branchCount: L(
    'Hozirda {count} ta filialimiz ishlaydi: {names}.',
    'Сейчас работает {count} филиалов: {names}.',
    'We currently have {count} branches: {names}.',
  ),
  branchList: L(
    'Filiallarimiz ({count} ta):\n{list}',
    'Наши филиалы ({count}):\n{list}',
    'Our branches ({count}):\n{list}',
  ),
  branchMissing: L(
    '{names} bo‘yicha filialimiz yo‘q. Mana ishlab turgan {count} ta filial:\n{list}',
    'Филиала в {names} у нас нет. Вот {count} действующих филиалов:\n{list}',
    'We don’t have a branch in {names}. Here are our {count} branches:\n{list}',
  ),
  branchOne: L(
    '{name} — {address}.{extra}',
    '{name} — {address}.{extra}',
    '{name} — {address}.{extra}',
  ),
  branchHours: L(' Ish vaqti: {hours}.', ' Часы работы: {hours}.', ' Working hours: {hours}.'),
  branchPhone: L(' Telefon: {phone}.', ' Телефон: {phone}.', ' Phone: {phone}.'),
  branchLandmark: L(' Mo‘ljal: {landmark}.', ' Ориентир: {landmark}.', ' Landmark: {landmark}.'),

  /* --- Kurslar ----------------------------------------------------------- */
  courseList: L(
    'Hozirda {count} ta kurs bor:\n{list}',
    'Сейчас доступно {count} курса:\n{list}',
    'We currently run {count} courses:\n{list}',
  ),
  courseLine: L(
    '• {title} — {age} yosh, {months} oy, haftasiga {lessons} dars.',
    '• {title} — {age} лет, {months} месяцев, {lessons} занятия в неделю.',
    '• {title} — ages {age}, {months} months, {lessons} lessons a week.',
  ),
  coursePrices: L(
    'Oylik to‘lov:\n{list}\nAniq shartlar va chegirmalarni menejer aytib beradi: {phone}',
    'Оплата за месяц:\n{list}\nТочные условия и скидки подскажет менеджер: {phone}',
    'Monthly fee:\n{list}\nA manager will confirm the exact terms and discounts: {phone}',
  ),
  coursePriceLine: L(
    '• {title} — oyiga {price} so‘m.',
    '• {title} — {price} сум в месяц.',
    '• {title} — {price} UZS per month.',
  ),
  courseOne: L(
    '{title} — {age} yosh. Dastur {months} oy, haftasiga {lessons} dars.{minutes}{price}',
    '{title} — {age} лет. Программа {months} месяцев, {lessons} занятия в неделю.{minutes}{price}',
    '{title} — ages {age}. The program runs {months} months, {lessons} lessons a week.{minutes}{price}',
  ),
  courseMinutes: L(
    ' Har bir dars {minutes} daqiqa.',
    ' Каждое занятие — {minutes} минут.',
    ' Each lesson lasts {minutes} minutes.',
  ),
  coursePriceTail: L(
    ' Oylik to‘lov — {price} so‘m.',
    ' Оплата — {price} сум в месяц.',
    ' The monthly fee is {price} UZS.',
  ),

  ageList: L(
    'Yosh bo‘yicha:\n{list}\nDastur bolaning yoshi va tayyorgarligiga qarab tanlanadi.',
    'По возрасту:\n{list}\nПрограмма подбирается по возрасту и подготовке ребёнка.',
    'By age:\n{list}\nThe program is chosen to match the child’s age and level.',
  ),
  ageLine: L('• {title} — {age} yosh.', '• {title} — {age} лет.', '• {title} — ages {age}.'),

  /* --- Dars jadvali ------------------------------------------------------ */
  schedule: L(
    'Darslar kichik guruhlarda o‘tadi:\n{list}\nAniq kun va soatni filial menejeri tanlaydi.',
    'Занятия проходят в малых группах:\n{list}\nТочный день и время подберёт менеджер филиала.',
    'Classes run in small groups:\n{list}\nThe branch manager will agree on the exact days and times.',
  ),
  scheduleLine: L(
    '• {title} — haftasiga {lessons} dars, jami {months} oy.{minutes}',
    '• {title} — {lessons} занятия в неделю, всего {months} месяцев.{minutes}',
    '• {title} — {lessons} lessons a week, {months} months in total.{minutes}',
  ),

  /* --- O'qituvchilar ----------------------------------------------------- */
  teacherList: L(
    'Saytda {count} ta o‘qituvchi profili bor:\n{list}',
    'На сайте {count} профиля преподавателей:\n{list}',
    'The site lists {count} teacher profiles:\n{list}',
  ),
  teacherLine: L(
    '• {name} — {badge}, {years} yillik tajriba.',
    '• {name} — {badge}, опыт {years} лет.',
    '• {name} — {badge}, {years} years of experience.',
  ),

  /* --- Vakansiyalar ------------------------------------------------------ */
  vacancyList: L(
    'Ochiq {count} ta vakansiya:\n{list}',
    'Открыто {count} вакансии:\n{list}',
    'There are {count} open positions:\n{list}',
  ),
  vacancyLine: L('• {title}{extra}', '• {title}{extra}', '• {title}{extra}'),
  vacancyOne: L(
    '{title}. {text}\nShartlar: {extra}.',
    '{title}. {text}\nУсловия: {extra}.',
    '{title}. {text}\nDetails: {extra}.',
  ),
  vacancyNone: L(
    'Hozircha ochiq vakansiya yo‘q. Yangi e’lonlar «Vakansiyalar» sahifasida chiqadi.',
    'Сейчас открытых вакансий нет. Новые появятся на странице «Вакансии».',
    'There are no open positions right now. New ones appear on the Vacancies page.',
  ),

  socialList: L(
    'Ijtimoiy tarmoqlarimiz:\n{list}',
    'Мы в соцсетях:\n{list}',
    'Find us on social media:\n{list}',
  ),

  /* --- Yangiliklar ------------------------------------------------------- */
  newsList: L('So‘nggi yangiliklar:\n{list}', 'Последние новости:\n{list}', 'Latest news:\n{list}'),
  newsLine: L('• {title} ({date})', '• {title} ({date})', '• {title} ({date})'),
}

/** Sahifadagi matndan javob topilganda oldiga qo'yiladigan gap. */
export const REPLY_SOURCE = L(
  'Sayt ma’lumotlariga ko‘ra: ',
  'По данным сайта: ',
  'According to the site: ',
)
