/**
 * «Направления» bo'limi ma'lumotlari.
 *
 * Yo'nalishlar soni oz va matni maketda qat'iy belgilangan (rasmlar ham
 * loyiha ichida), shuning uchun kontent admin paneldan emas, shu fayldan
 * olinadi — `spacePlatform.js` bilan bir xil yondashuv.
 */
import { L } from '@/i18n/localize'

import itKidsImage from '@/assets/images/ItKids.webp'
import itDevImage from '@/assets/images/dasturlash.webp'

import cppIcon from '@/assets/icons/tech-cpp.svg'
import cssIcon from '@/assets/icons/tech-css.svg'
import htmlIcon from '@/assets/icons/tech-html.svg'
import jsIcon from '@/assets/icons/tech-js.svg'
import pythonIcon from '@/assets/icons/tech-python.svg'
import reactIcon from '@/assets/icons/tech-react.svg'

/** Kartochkalardagi texnologiya yorliqlari. */
export const TECH = {
  html: { label: 'HTML', icon: htmlIcon },
  css: { label: 'CSS', icon: cssIcon },
  js: { label: 'JavaScript', icon: jsIcon },
  react: { label: 'React', icon: reactIcon },
  python: { label: 'Python', icon: pythonIcon },
  cpp: { label: 'C++', icon: cppIcon },
}

export const DIRECTIONS = [
  {
    slug: 'it-kids',
    title: 'IT Kids',
    subtitle: L(
      'Robototexnika orqali IT olamiga birinchi qadamlar',
      'Первые шаги в мир IT через робототехнику',
      'First steps into IT through robotics',
    ),
    description: L(
      'Bola IT’ni o‘yin orqali o‘rganadi — robotlar yig‘adi, dasturlaydi va aqlli uy yaratadi. C++ va Python’ni o‘zlashtiradi, Arduino bilan ishlaydi.',
      'Ребёнок изучает IT через игру — собирает роботов, программирует и создаёт умные дома. Осваивает C++ и Python, работает с Arduino.',
      'Children learn IT through play — building robots, writing code and creating smart homes. They pick up C++ and Python and work with Arduino.',
    ),
    image: itKidsImage,
    tech: ['html', 'css', 'js'],
    ageRange: L('9–11 yosh', '9–11 лет', 'ages 9–11'),
  },
  {
    slug: 'it-razrabotka',
    title: L('IT-dasturlash', 'IT-разработка', 'IT Development'),
    subtitle: L(
      'Saytlar, botlar va sun’iy intellekt — hammasi bitta kursda',
      'Сайты, боты и ИИ — всё в одном курсе',
      'Websites, bots and AI — all in one course',
    ),
    description: L(
      'Bola saytlar va Telegram-botlar yaratishni, ma’lumotlar bazasi bilan ishlashni va sun’iy intellektdan foydalanishni o‘rganadi. Dasturlashning mustahkam poydevorini va dasturchi tafakkurini shakllantiradi.',
      'Ребёнок научится создавать сайты, Telegram-боты, работать с базами данных и использовать ИИ. Формирует прочную базу программирования и мышления разработчика.',
      'Children learn to build websites and Telegram bots, work with databases and use AI. They build a solid programming foundation and a developer’s way of thinking.',
    ),
    image: itDevImage,
    tech: ['html', 'css', 'js', 'react'],
    ageRange: L('12–17 yosh', '12–17 лет', 'ages 12–17'),
  },
]

/** Tayyorlanayotgan yo'nalishlar haqidagi banner. */
export const COMING_SOON = {
  title: L('Tez orada...', 'Скоро...', 'Coming soon...'),
  description: L(
    'Yangi yo‘nalishlar tayyorlanmoqda: AI, Game Development, Design va kengaytirilgan Robotics.',
    'Готовим новые направления: AI, Game Development, Design и расширенную Robotics.',
    'New tracks are on the way: AI, Game Development, Design and extended Robotics.',
  ),
}
