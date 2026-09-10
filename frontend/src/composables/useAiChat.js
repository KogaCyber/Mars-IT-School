/**
 * AI yordamchisi bilan suhbat holati.
 *
 * Holat modul darajasida — panelni istalgan joydan ochish mumkin
 * (`openAiChat()`), ko'rsatishni esa `App.vue`dagi bitta `AiAssistant`
 * komponenti bajaradi (`useVideoModal` bilan bir xil yondashuv).
 *
 * Javoblar `utils/assistant.js` da, sayt ma'lumotlari asosida hisoblanadi:
 * filiallar, kurslar, narxlar va boshqalar chat birinchi ochilganda yuklanadi
 * (`utils/assistantData.js`). Javob qisqa «yozmoqda…» pauzasidan keyin
 * chiqadi — suhbat jonli ko'rinadi.
 */
import { computed, ref, watch } from 'vue'

import { ASSISTANT_QUICK } from '@/data/assistantFaq'
import { i18n, t } from '@/i18n'
import { localize } from '@/i18n/localize'
import { useSiteStore } from '@/stores/site'
import { answerQuestion, topicById } from '@/utils/assistant'
import { loadAssistantData } from '@/utils/assistantData'

/** «Yozmoqda…» pauzasi: qisqa javob tez, uzunrog'i biroz kechroq keladi. */
const TYPING_MIN = 450
const TYPING_MAX = 1300

const isOpen = ref(false)
const isTyping = ref(false)
/** @type {import('vue').Ref<Array<{id: number, role: 'bot'|'user', text: string, links: Array}>>} */
const messages = ref([])
/** Tashrifchi panelni hech ochmagan bo'lsa — tanishtiruvchi bulutcha chiqadi. */
const wasOpened = ref(false)

let nextId = 0
let typingTimer = null
/** Har bir savolning tartib raqami — eskirgan javob chatga tushmasligi uchun. */
let askId = 0

function push(role, text, links = []) {
  messages.value.push({ id: ++nextId, role, text, links })
}

function greet() {
  push('bot', t('assistant.greeting'))
}

function stopTyping() {
  clearTimeout(typingTimer)
  typingTimer = null
  isTyping.value = false
}

/** Suhbatni boshidan boshlaydi (til almashganda ham shu chaqiriladi). */
export function resetAiChat() {
  askId += 1
  stopTyping()
  messages.value = []
  greet()
}

export function openAiChat() {
  isOpen.value = true
  wasOpened.value = true
  if (messages.value.length === 0) greet()
  // Birinchi savolgacha ma'lumot tayyor bo'lsin.
  loadAssistantData(i18n.global.locale.value)
}

export function closeAiChat() {
  isOpen.value = false
  stopTyping()
}

/**
 * Savol yuborish.
 *
 * @param {string} question foydalanuvchi matni
 * @param {string} [topicId] chiplar uchun: javob mavzusi oldindan ma'lum,
 *        shu sababli kalit so'z qidirilmaydi
 */
export async function askAiChat(question, topicId) {
  const text = String(question || '').trim()
  if (!text) return

  push('user', text)
  stopTyping()
  isTyping.value = true

  const id = ++askId
  const locale = i18n.global.locale.value
  // Filiallar, kurslar, narxlar — javob shu ro'yxatlardan yig'iladi.
  const data = await loadAssistantData(locale)
  // Kutish paytida suhbat tozalangan yoki yangi savol yuborilgan bo'lishi mumkin.
  if (id !== askId) return

  const { settings } = useSiteStore()
  const answer = answerQuestion(text, {
    locale,
    settings,
    data,
    topic: topicId ? topicById(topicId) : null,
  })
  const delay = Math.min(TYPING_MAX, TYPING_MIN + answer.text.length * 4)

  typingTimer = setTimeout(() => {
    isTyping.value = false
    typingTimer = null
    push('bot', answer.text, answer.links)
  }, delay)
}

// Til almashganda eski tildagi suhbat qolib ketmasin.
watch(
  () => i18n.global.locale.value,
  () => {
    if (messages.value.length) resetAiChat()
  },
)

export function useAiChat() {
  const locale = computed(() => i18n.global.locale.value)

  /** Suhbat boshida taklif qilinadigan savollar. */
  const quickQuestions = computed(() =>
    ASSISTANT_QUICK.map((id) => topicById(id))
      .filter((topic) => topic?.chip)
      .map((topic) => ({ id: topic.id, label: localize(topic.chip, locale.value) })),
  )

  /** Chiplar faqat suhbat boshida kerak — keyin joyni band qilmaydi. */
  const showQuick = computed(() => messages.value.filter((m) => m.role === 'user').length === 0)

  return {
    isOpen,
    isTyping,
    messages,
    wasOpened,
    quickQuestions,
    showQuick,
    open: openAiChat,
    close: closeAiChat,
    toggle: () => (isOpen.value ? closeAiChat() : openAiChat()),
    ask: askAiChat,
    reset: resetAiChat,
  }
}
