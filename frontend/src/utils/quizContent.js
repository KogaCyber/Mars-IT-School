/**
 * Natija sahifasining matnlarini foydalanuvchining javoblariga moslaydi.
 *
 * Backend uchta narsani qaytaradi: g'olib yo'nalish (`outcome`), yo'nalishlar
 * bo'yicha moslik foizi (`matches`) va ko'nikmalar tahlili (`skills`). Shu
 * uchtasidan sahifadagi barcha matnlar yig'iladi:
 *
 *   • sarlavha va izoh — foizlar va eng kuchli ko'nikmalar bilan,
 *   • «Qobiliyatlar tahlili» blokidagi ustunliklar — aynan shu bolaning
 *     birinchi va ikkinchi kuchli tomoni,
 *   • xulosa — o'sish zonasi (eng past ko'nikma) bilan.
 *
 * Yo'nalishga bog'liq o'zgarmas qismlar (o'qish yo'li, reja) `quizOutcomes.js`
 * dan olinadi va joriy tilga `localize()` bilan o'giriladi. Dinamik jumlalar
 * esa `i18n/messages/quiz.js` dagi shablonlardan yig'iladi — shuning uchun
 * funksiya `t` va `locale` ni tashqaridan oladi (`useQuizContent`).
 */
import { computed, unref } from 'vue'
import { useI18n } from 'vue-i18n'

import { QUIZ_OUTCOME_DETAILS, SKILL_STRENGTHS } from '@/data/quizOutcomes'
import { localize } from '@/i18n/localize'

/** Ro'yxatni «a, b va c» ko'rinishida birlashtiradi (bog'lovchi tildan olinadi). */
function joinList(items, conjunction) {
  if (items.length < 2) return items[0] || ''
  return `${items.slice(0, -1).join(', ')} ${conjunction} ${items[items.length - 1]}`
}

/** «Логическое мышление» → «логическое мышление (100%)» */
function skillPhrase(skill) {
  return `${skill.title.charAt(0).toLowerCase()}${skill.title.slice(1)} (${skill.percent}%)`
}

/**
 * @param {{ outcome: Object|null, matches: Array, skills: Array }} result
 * @param {{ t: Function, locale: string }} i18n joriy til va tarjima funksiyasi
 * @returns {Object} sahifa kutayotgan tuzilma (`label`, `headline`, `steps`, `profile`, …)
 */
export function buildQuizContent({ outcome, matches = [], skills = [] }, { t, locale }) {
  const code = outcome?.code === 'backend' ? 'backend' : 'frontend'
  const base = localize(QUIZ_OUTCOME_DETAILS[code], locale)
  const strengths = localize(SKILL_STRENGTHS, locale)

  const name = code === 'backend' ? 'Backend' : 'Frontend'
  const own = matches.find((item) => item.code === code)?.percent ?? 0
  const other = matches.find((item) => item.code !== code)?.percent ?? 0
  const gap = own - other

  /** Foizlar yaqin bo'lsa — xulosa ham ehtiyotkor bo'ladi. */
  const isClose = matches.length > 1 && gap <= 6
  const isStrong = gap >= 25

  // Kuchli tomonlar: foizi 0 dan katta bo'lganlari (backend allaqachon saralagan)
  const strong = skills.filter((item) => item.percent > 0)
  const [first, second] = strong
  const weakest = skills.length ? skills[skills.length - 1] : null

  /** Natija aniqlanmagan bo'lsa (javoblar hisobga olinmagan) — o'zgarmas matn. */
  const hasResult = Boolean(outcome) && matches.length > 0

  /** Backend'da sarlavha «…, Frontend'dan boshlash kerak!» bilan tugaydi. */
  const tail = code === 'backend' ? t('quiz.tailBackend') : t('quiz.tailPlain')

  const headline = !hasResult
    ? base.headline
    : isClose
      ? t('quiz.headlineClose', { own, other, name, tail })
      : t('quiz.headlineMain', { name, own, tail })

  const conjunction = t('quiz.listJoin')

  const description = strong.length
    ? t('quiz.descriptionStrong', {
        skills: joinList(strong.slice(0, 3).map(skillPhrase), conjunction),
        rest: base.description.split('. ').slice(1).join('. '),
      })
    : base.description

  // Ustunliklar ro'yxati: birinchi ikkitasi — shu bolaning kuchli tomonlari
  const points = [...base.profile.points]
  if (first) {
    points[0] = {
      text: `${first.title} — ${first.percent}%. ${strengths[first.code] || ''}`.trim(),
      icon: 'chart',
    }
  }
  if (second) {
    points[1] = {
      text: `${second.title} — ${second.percent}%. ${strengths[second.code] || ''}`.trim(),
      icon: 'logic',
    }
  }

  const intro = strong.length
    ? t('quiz.introStrong', {
        skills: joinList(
          strong.slice(0, 3).map((item) => item.title.toUpperCase()),
          conjunction,
        ),
        name,
      })
    : base.profile.intro

  return {
    ...base,
    label: hasResult && isStrong ? t('quiz.confidentDirection') : base.label,
    headline,
    description,
    profile: { ...base.profile, intro, points },
    /** «Test natijasining yakuni» blokidagi qo'shimcha qator. */
    growthSkill: weakest && weakest.percent < 50 ? weakest : null,
  }
}

/**
 * Reaktiv variant: til almashganda barcha matnlar o'zi qayta hisoblanadi.
 * @param {import('vue').Ref|Object} source `{ outcome, matches, skills }`
 */
export function useQuizContent(source) {
  const { t, locale } = useI18n()
  return computed(() => buildQuizContent(unref(source) || {}, { t, locale: locale.value }))
}
