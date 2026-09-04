/**
 * Jonli kontent — admin paneldagi o'zgarish sahifani yangilamasdan ko'rinadi.
 *
 * Backend kontentning «versiyasini» saqlaydi va har qanday o'zgarishda uni
 * ko'taradi (`apps/core/revision.py`). Bu yerda shu raqam qisqa oraliqda
 * so'rab turiladi: o'zgargani sezilsa, ochiq sahifadagi barcha yuklovchilar
 * qaytadan ishga tushadi (`useAsyncData`) va sayt sozlamalari yangilanadi.
 *
 * Nega SSE/WebSocket emas: backend gunicorn'ning `gthread` rejimida ishlaydi
 * va bir vaqtda ochiq ulanishlar soni cheklangan — uzoq ulanishlar tez orada
 * barcha oqimlarni band qilib qo'yardi. Kichik JSON so'rovi esa serverning
 * xotirasidan javob oladi va deyarli hech narsa turmaydi.
 *
 * So'rovlar faqat sahifa ko'rinib turganda yuboriladi: fon oynasi bekorga
 * trafik sarflamaydi, foydalanuvchi qaytgan zahoti esa darhol tekshiriladi.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { setContentVersion } from '@/api/contentVersion'
import { fetchRevision } from '@/api/revision'

/** Versiya shuncha millisekundda bir tekshiriladi. */
const POLL_INTERVAL_MS = 5000

export const useLiveStore = defineStore('live', () => {
  /** Oxirgi ma'lum versiya (0 — hali noma'lum). */
  const revision = ref(0)

  const listeners = new Set()
  let timer = 0
  let isChecking = false
  let isStarted = false

  /**
   * Versiya o'zgarganda chaqiriladigan funksiyani ro'yxatga qo'shadi.
   * @returns {() => void} obunani bekor qiluvchi funksiya
   */
  function subscribe(handler) {
    listeners.add(handler)
    return () => listeners.delete(handler)
  }

  async function check() {
    if (isChecking || document.visibilityState === 'hidden') return
    isChecking = true
    try {
      const next = await fetchRevision()
      if (!next || next === revision.value) return

      const isFirst = revision.value === 0
      revision.value = next
      setContentVersion(next)
      // Birinchi javob — shunchaki boshlang'ich qiymat, kontent endi yuklandi.
      if (!isFirst) listeners.forEach((handler) => handler())
    } catch {
      // Tarmoq uzilgan bo'lishi mumkin — keyingi urinishda tekshiriladi.
    } finally {
      isChecking = false
    }
  }

  function onVisibility() {
    // Boshqa ilovadan qaytilganda kutib o'tirmasdan tekshiramiz.
    if (document.visibilityState === 'visible') check()
  }

  /** Kuzatuvni boshlaydi (ilova ishga tushganda bir marta chaqiriladi). */
  function start() {
    if (isStarted) return
    isStarted = true
    check()
    timer = window.setInterval(check, POLL_INTERVAL_MS)
    document.addEventListener('visibilitychange', onVisibility)
    window.addEventListener('focus', onVisibility)
  }

  function stop() {
    isStarted = false
    window.clearInterval(timer)
    document.removeEventListener('visibilitychange', onVisibility)
    window.removeEventListener('focus', onVisibility)
  }

  return { revision, subscribe, start, stop, check }
})
