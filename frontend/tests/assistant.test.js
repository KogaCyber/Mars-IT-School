/**
 * AI yordamchisining javob topishi.
 *
 * Asosiy shart: javob sayt ma'lumotlaridan olinadi. Shuning uchun testlar
 * API'dan olingan haqiqiy yozuvlar (`fixtures/assistantData.json`) ustida
 * ishlaydi va javobdagi raqamlar shu yozuvlarga mos kelishini tekshiradi.
 *
 * Alohida e'tibor xato yozilgan savollarga: tashrifchi «filliallar» deb ham,
 * «Чиланзар» deb ham yozadi — ikkalasi ham topilishi kerak.
 */
import { describe, expect, it } from 'vitest'

import data from './fixtures/assistantData.json'

import { answerQuestion } from '@/utils/assistant'

const settings = {
  phone: '+998 78 777 77 57',
  telegram_url: 'https://t.me/marsitschool',
  email: 'info@mars.uz',
}

const ask = (question, locale = 'uz') => answerQuestion(question, { locale, settings, data })

describe('filiallar bo‘yicha savollar', () => {
  it('sonini haqiqiy ro‘yxatdan aytadi', () => {
    const answer = ask('Nechta filliallar mavjud')
    expect(answer.id).toBe('branch-count')
    expect(answer.text).toContain(String(data.branches.length))
    expect(answer.text).toContain(data.branches[0].name)
  })

  it('yo‘q filialni yo‘q deydi va borlarini ko‘rsatadi', () => {
    const answer = ask('Yashnabod, Qibray va Oybek filliallari bormi')
    expect(answer.id).toBe('branch-missing')
    expect(answer.text).toContain('Yashnabod')
    expect(answer.text).toContain('Qibray')
    expect(answer.text).toContain(data.branches[1].name)
  })

  it('fe’lni joy nomi deb o‘ylamaydi', () => {
    // «ochasizmi» — nom emas, shuning uchun javobda turmasligi kerak.
    expect(ask('Qibrayda filial ochasizmi').text).not.toContain('Ochasiz')
  })

  it('nomi xato yozilgan filialni ham topadi', () => {
    const answer = ask('Chilanzarda filial bormi')
    expect(answer.id).toBe('branch-detail')
    expect(answer.text).toContain('Chilonzor')
  })

  it('kirillcha yozilgan nomni ham topadi', () => {
    const answer = ask('Есть ли филиал в Чиланзаре', 'ru')
    expect(answer.id).toBe('branch-detail')
    expect(answer.text).toContain('Chilonzor')
  })

  it('manzil va ish vaqtini beradi', () => {
    const branch = data.branches[0]
    const answer = ask(`${branch.name} manzili qanday`)
    expect(answer.text).toContain(branch.address)
    expect(answer.text).toContain(branch.working_hours)
    expect(answer.links[0]).toMatchObject({ name: 'branch', params: { slug: branch.slug } })
  })
})

describe('kurslar bo‘yicha savollar', () => {
  it('narxni API’dagi qiymatdan aytadi', () => {
    const answer = ask('Narxi qancha')
    expect(answer.id).toBe('course-price')
    // 1090000 → «1 090 000» (bo'shliq — ajratuvchi).
    expect(answer.text.replace(/\s/g, '')).toContain('1090000')
  })

  it('yosh oralig‘i kurslar ma’lumotidan olinadi', () => {
    const answer = ask('Necha yoshdan qabul qilasiz')
    expect(answer.id).toBe('course-age')
    expect(answer.text).toContain(data.courses[0].age_range)
  })

  it('kurslar ro‘yxatini beradi', () => {
    const answer = ask('Qanday kurslar bor')
    expect(answer.text).toContain(data.courses[0].title)
    expect(answer.text).toContain(String(data.courses[0].duration_months))
  })

  it('kurs nomi aytilsa — o‘sha kurs haqida', () => {
    const answer = ask('IT Kids haqida aytib bering')
    expect(answer.text).toContain(data.courses[0].age_range)
    expect(answer.links[0]).toMatchObject({ name: 'course' })
  })
})

describe('boshqa bo‘limlar', () => {
  it('vakansiyani nomi bo‘yicha topadi', () => {
    const answer = ask('Kurator vakansiyasi haqida')
    expect(answer.id).toBe('vacancy-detail')
    expect(answer.text).toContain('Kurator')
  })

  it('o‘qituvchilar ro‘yxatini beradi', () => {
    const answer = ask('Кто преподает', 'ru')
    expect(answer.id).toBe('teachers')
    expect(answer.text).toContain(data.teachers[0].full_name)
  })

  it('yangiliklarni sanasi bilan beradi', () => {
    const answer = ask('Oxirgi yangiliklar')
    expect(answer.id).toBe('news')
    expect(answer.text).toContain(data.news[0].title)
  })

  it('ijtimoiy tarmoq havolasini sozlamalardan oladi', () => {
    const answer = ask('Telegramingiz bormi')
    expect(answer.text).toContain(settings.telegram_url)
  })

  it('kontaktlarni sozlamalardan to‘ldiradi', () => {
    const answer = ask('Telefon raqamingiz')
    expect(answer.text).toContain(settings.phone)
  })
})

describe('javob topilmaganda', () => {
  it('o‘ylab topmaydi — menejerga yo‘naltiradi', () => {
    // Saytda sertifikat haqida ma'lumot yo'q, demak javob ham bo'lmasligi kerak.
    const answer = ask('Sertifikat berasizlarmi')
    expect(answer.id).toBe('fallback')
    expect(answer.links.map((link) => link.name)).toContain('application')
  })

  it('tasodifiy matnga javob o‘ylab topmaydi', () => {
    expect(ask('asdfgh qwerty').id).toBe('fallback')
  })

  it('ma’lumot yuklanmagan bo‘lsa ham ishlaydi', () => {
    // API yiqilgan holat: javob tayyor matnlardan keladi.
    const answer = answerQuestion('Sinov darsi bormi', { locale: 'uz', settings })
    expect(answer.id).toBe('trial')
    expect(answer.text.length).toBeGreaterThan(0)
  })
})

describe('salomlashuv', () => {
  it('salomga javob beradi', () => {
    expect(ask('Salom').id).toBe('greeting')
  })
})
