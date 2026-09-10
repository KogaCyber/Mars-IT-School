/**
 * Yordamchining qidiruv qismi: matnni tokenlarga bo'lish va xato yozilgan
 * so'zlarni ham topish.
 *
 * Nega oddiy `includes()` yetmaydi:
 *
 *   • O'zbek tilida so'z qo'shimchalar bilan o'zgaradi — «filial», «filiallar»,
 *     «filiallari», «filialingiz». Shu sababli qo'shimchalar kesiladi (`stem`).
 *   • Tashrifchi shoshib yozadi: «filliallar», «Chilanzar», «kurslari».
 *     Shuning uchun tokenlar Levenshtein masofasi bilan solishtiriladi —
 *     bitta-ikkita harf farqi javobni yo'qotmaydi.
 *   • Savolda ma'nosiz so'zlar ko'p («menga», «eng», «shu yerda») — ular
 *     to'xtatuv so'zlar ro'yxatida va bahoga ta'sir qilmaydi.
 */

/**
 * Kirill harflari lotinchaga o'giriladi.
 *
 * Sabab: filial nomlari bazada lotincha («Chilonzor filiali»), tashrifchi esa
 * ruscha sahifada kirillcha yozadi («Чиланзар»). O'girilgandan keyin ikkalasi
 * bir alifboda bo'ladi va solishtirish ishlaydi. Yon foydasi — «филиал» va
 * «filial» kabi kalit so'zlar ham birlashadi.
 */
const CYRILLIC = {
  а: 'a',
  б: 'b',
  в: 'v',
  г: 'g',
  д: 'd',
  е: 'e',
  ж: 'j',
  з: 'z',
  и: 'i',
  й: 'y',
  к: 'k',
  л: 'l',
  м: 'm',
  н: 'n',
  о: 'o',
  п: 'p',
  р: 'r',
  с: 's',
  т: 't',
  у: 'u',
  ф: 'f',
  х: 'x',
  ц: 'ts',
  ч: 'ch',
  ш: 'sh',
  щ: 'sh',
  ъ: '',
  ы: 'i',
  ь: '',
  э: 'e',
  ю: 'yu',
  я: 'ya',
  ғ: 'g',
  қ: 'q',
  ҳ: 'h',
  ў: 'o',
}

function translit(text) {
  return text.replace(/[\u0400-\u04ff]/g, (letter) => CYRILLIC[letter] ?? letter)
}

/** Baholashda hisobga olinmaydigan so'zlar (uz / ru / en). */
const RAW_STOP_WORDS = [
  // uz
  'va',
  'bilan',
  'uchun',
  'ham',
  'yoki',
  'lekin',
  'ammo',
  'shu',
  'bu',
  'u',
  'men',
  'menga',
  'meni',
  'mening',
  'siz',
  'sizga',
  'sizning',
  'biz',
  'bizga',
  'eng',
  'juda',
  'yana',
  'faqat',
  'kerak',
  'haqida',
  'haqda',
  'mumkin',
  'iltimos',
  'ayting',
  'aytib',
  'bering',
  'boradi',
  'bo',
  'yerda',
  'joy',
  'joylar',
  'joyi',
  'nima',
  'qanday',
  'qaysi',
  'kim',
  'yaqin',
  'yaxshi',
  'salom',
  'xayr',
  // ru
  'и',
  'или',
  'но',
  'а',
  'для',
  'с',
  'со',
  'на',
  'в',
  'во',
  'по',
  'из',
  'у',
  'мне',
  'меня',
  'мой',
  'вы',
  'вас',
  'ваш',
  'мы',
  'нам',
  'это',
  'этот',
  'тут',
  'здесь',
  'там',
  'самый',
  'очень',
  'ещё',
  'еще',
  'только',
  'нужно',
  'можно',
  'пожалуйста',
  'скажите',
  'подскажите',
  'про',
  'что',
  'какой',
  'какие',
  'как',
  'кто',
  'ближе',
  'ближайший',
  'хорошо',
  'привет',
  // en
  'and',
  'or',
  'but',
  'for',
  'with',
  'the',
  'a',
  'an',
  'to',
  'of',
  'in',
  'on',
  'at',
  'my',
  'me',
  'i',
  'you',
  'your',
  'we',
  'us',
  'this',
  'that',
  'here',
  'there',
  'very',
  'also',
  'only',
  'need',
  'can',
  'please',
  'tell',
  'what',
  'which',
  'how',
  'who',
  'near',
  'nearest',
  'good',
  'hello',
  'is',
  'are',
  'do',
  'does',
  'have',
  'has',
]

/** Ro'yxat ham savol bilan bir xil ko'rinishga keltiriladi. */
export const STOP_WORDS = new Set(RAW_STOP_WORDS.map((word) => translit(word)))

/**
 * Qo'shimchalar — uzunidan qisqasiga qarab kesiladi.
 * Faqat o'zak kamida 4 harf qolsa kesiladi, aks holda «kurs» → «ku» bo'lib
 * ketardi va hamma narsaga o'xshab qolardi.
 */
const RAW_SUFFIXES = [
  // uz
  'larimizda',
  'laringizda',
  'larimiz',
  'laringiz',
  'laridan',
  'lariga',
  'larida',
  'larini',
  'larning',
  'lardan',
  'larga',
  'larda',
  'larni',
  'lari',
  'lar',
  'ning',
  'imiz',
  'ingiz',
  'dagi',
  'dan',
  'gan',
  'ga',
  'da',
  'ni',
  'si',
  'im',
  'ingiz',
  'ib',
  'mi',
  // ru
  'ами',
  'ями',
  'ов',
  'ев',
  'ах',
  'ях',
  'ами',
  'ой',
  'ый',
  'ий',
  'ая',
  'ые',
  'ам',
  'ям',
  'ом',
  'ем',
  'а',
  'ы',
  'и',
  'у',
  'ю',
  'е',
  // en
  'ies',
  'es',
  's',
]

/** Kirillcha qo'shimchalar ham lotinchada solishtiriladi. */
const SUFFIXES = RAW_SUFFIXES.map((suffix) => translit(suffix))

/** Matnni solishtirishga tayyorlaydi: kichik harf, apostrofsiz, belgisiz. */
export function normalize(text) {
  return String(text || '')
    .toLowerCase()
    .replace(/[‘’'`ʻʼ]/g, '')
    .replace(/ё/g, 'е')
    .replace(/[\u0400-\u04ff]+/g, translit)
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim()
}

/** So'zning o'zagi (qo'shimchasi kesilgan ko'rinishi). */
export function stem(word) {
  let value = word
  for (const suffix of SUFFIXES) {
    if (value.length - suffix.length >= 4 && value.endsWith(suffix)) {
      value = value.slice(0, -suffix.length)
      break
    }
  }
  return value
}

/**
 * Matn → mazmunli o'zaklar ro'yxati.
 *
 * Savol butunlay to'xtatuv so'zlardan iborat bo'lsa («nima qilay?»), ular
 * baribir qaytariladi — aks holda qidiradigan narsa qolmasdi.
 */
export function tokenize(text, { keepStopWords = false } = {}) {
  const words = normalize(text)
    .split(' ')
    .filter((word) => word.length > 1)

  const meaningful = keepStopWords ? words : words.filter((word) => !STOP_WORDS.has(word))
  return (meaningful.length > 0 ? meaningful : words).map(stem)
}

/** Levenshtein masofasi; `limit` dan oshsa hisoblash to'xtaydi. */
export function distance(a, b, limit = 2) {
  if (a === b) return 0
  if (Math.abs(a.length - b.length) > limit) return limit + 1

  let previous = Array.from({ length: b.length + 1 }, (unused, index) => index)

  for (let i = 1; i <= a.length; i += 1) {
    const current = [i]
    let best = i
    for (let j = 1; j <= b.length; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1
      current[j] = Math.min(current[j - 1] + 1, previous[j] + 1, previous[j - 1] + cost)
      best = Math.min(best, current[j])
    }
    if (best > limit) return limit + 1
    previous = current
  }

  return previous[b.length]
}

/**
 * Ikki o'zakning o'xshashligi: 0 (mos emas) … 1 (aynan bir xil).
 * «fillial» ↔ «filial» yoki «chilanzar» ↔ «chilonzor» kabi xatolar 0 emas.
 */
export function similarity(a, b) {
  if (!a || !b) return 0
  if (a === b) return 1

  const short = a.length <= b.length ? a : b
  const long = a.length <= b.length ? b : a
  if (short.length >= 4 && long.startsWith(short)) return 0.9

  if (short.length >= 4 && distance(a, b, 1) <= 1) return 0.8
  if (short.length >= 7 && distance(a, b, 2) <= 2) return 0.6

  return 0
}

/** Token ro'yxatida so'zga eng o'xshashini topadi. */
export function bestMatch(token, tokens) {
  let best = 0
  for (const candidate of tokens) {
    const score = similarity(token, candidate)
    if (score > best) best = score
    if (best === 1) break
  }
  return best
}

/** Ro'yxatdagi biror so'z savolda uchraydimi (xato yozilgan bo'lsa ham). */
export function mentions(queryTokens, words) {
  const targets = words.flatMap((word) => tokenize(word, { keepStopWords: true }))
  return queryTokens.some((token) => bestMatch(token, targets) >= 0.8)
}

/**
 * Hujjatlar ichidan savolga eng mos kelganini topadi.
 *
 * @param {string} question
 * @param {Array<{title?: string, text?: string}>} documents
 * @param {number} [threshold] shu bahodan pastlari e'tiborsiz qoldiriladi
 */
export function findBest(question, documents, threshold = 0.45) {
  const queryTokens = tokenize(question)
  if (queryTokens.length === 0) return null

  let best = null
  let bestScore = 0

  for (const document of documents) {
    const titleTokens = tokenize(document.title || '')
    const textTokens = tokenize(document.text || '')
    if (titleTokens.length === 0 && textTokens.length === 0) continue

    let score = 0
    // Savoldagi HAR BIR uzun so'z hujjatda uchrashi shart. Aks holda
    // «sertifikat berasizlarmi» savoliga «…dars beradi» degan vakansiya
    // matni javob bo'lib chiqardi: gap faqat «ber» so'ziga o'xshaganidan.
    let hasUnmatchedKeyWord = false

    for (const token of queryTokens) {
      const title = bestMatch(token, titleTokens)
      const text = bestMatch(token, textTokens)
      if (token.length >= 5 && Math.max(title, text) < 0.5) hasUnmatchedKeyWord = true
      // Sarlavhadagi moslik matn ichidagisidan qimmatroq.
      score += Math.max(title * 1.6, text)
    }
    score /= queryTokens.length

    if (!hasUnmatchedKeyWord && score > bestScore) {
      best = document
      bestScore = score
    }
  }

  return bestScore >= threshold ? { ...best, score: bestScore } : null
}
