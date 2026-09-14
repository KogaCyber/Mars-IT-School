/**
 * Sayt sahifalarining tahrirlanadigan kontenti (sarlavhalar, matnlar, rasmlar).
 *
 * Har bir blok admin panelda «bo'lim» sifatida turadi va shu yerga kaliti
 * bo'yicha tushadi (`home.hero`, `itkids.stages`, …). Komponentlar uni
 * `useSection()` orqali o'qiydi.
 *
 * Bo'sh maydon — «maketdagi standart matn qolsin» degani: `useSection()`
 * bunday joyda tarjima faylidagi qiymatni ko'rsatadi. Shu tufayli admin
 * panelda hech narsa yozilmagan (yoki backend javob bermagan) holatda ham
 * sayt to'liq ko'rinadi.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { fetchContent } from '@/api/content'

/** Topilmagan bo'lim uchun — komponentlar `undefined` bilan ovora bo'lmasin. */
export const EMPTY_SECTION = Object.freeze({ items: [] })

export const useContentStore = defineStore('content', () => {
  /** @type {import('vue').Ref<Record<string, any>>} */
  const sections = ref({})
  const isLoaded = ref(false)

  /**
   * Muharrir «jonli ko'rish» qatlami: xodim panelda matn/rasmni o'zgartirsa,
   * o'zgarish shu yerga yoziladi va sahifada darhol ko'rinadi (hali saqlanmagan
   * bo'lsa ham). Serverdan qayta yuklash (`load`) buni TEGMAYDI — shuning uchun
   * fon so'rovi tahrirni ustidan yozib yubormaydi. «Сохранить»/«Отмена» bosilgach
   * qatlam tozalanadi: saqlangan bo'lsa — server qiymati, aks holda — eskisi qoladi.
   * @type {import('vue').Ref<Record<string, any>>}
   */
  const overrides = ref({})

  // Til almashganda va admin panelda kontent o'zgarganda qayta yuklanadi —
  // javoblar esa yuborilgan tartibda qaytmaydi. Faqat oxirgi so'rov qabul
  // qilinadi, aks holda sekinroq eski javob yangisining ustiga yozilardi.
  let requestId = 0

  async function load({ force = false } = {}) {
    if (isLoaded.value && !force) return
    const id = ++requestId
    try {
      const data = await fetchContent()
      if (id === requestId && data) sections.value = data
    } catch {
      // Kontent yuklanmasa sayt maketdagi matn bilan ishlashda davom etadi.
    } finally {
      if (id === requestId) isLoaded.value = true
    }
  }

  /** Boshqa so'rov bilan birga kelgan bo'limlarni qo'shadi (masalan `/home/`). */
  function merge(payload) {
    if (payload && typeof payload === 'object') {
      sections.value = { ...sections.value, ...payload }
    }
  }

  function get(key) {
    return overrides.value[key] ?? sections.value[key] ?? EMPTY_SECTION
  }

  /** Serverdan kelgan asl qiymat (jonli ko'rish qatlamisiz). */
  function raw(key) {
    return sections.value[key] ?? EMPTY_SECTION
  }

  /** Jonli ko'rishni o'rnatadi yoki (value=null bo'lsa) tozalaydi. */
  function setPreview(key, value) {
    const next = { ...overrides.value }
    if (value == null) delete next[key]
    else next[key] = value
    overrides.value = next
  }

  return { sections, isLoaded, load, merge, get, raw, setPreview }
})
