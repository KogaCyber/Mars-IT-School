/**
 * Admin paneldan boshqariladigan sahifa bo'limini o'qish.
 *
 *   const hero = useSection('home.hero', {
 *     title: 'home.heroTitle',        // admin panelda bo'sh bo'lsa — shu tarjima
 *     text: 'home.heroText',
 *   })
 *
 *   hero.title        // matn
 *   hero.titleLines   // qatorlarga bo'lingan sarlavha (maketda ko'p qatorli)
 *   hero.image        // admin panelda yuklangan rasm yoki null
 *   hero.items        // ichki kartochkalar/bosqichlar ro'yxati
 *
 * Nega fallback kerak: bo'lim matni admin panelda bo'sh qoldirilishi mumkin
 * (yoki backend javob bermasligi mumkin) — bunday holatda sayt bo'sh sarlavha
 * ko'rsatmasligi, maketdagi matn bilan ishlashda davom etishi kerak.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { useContentStore } from '@/stores/content'

/** Admin paneldagi matn maydonlari → `useSection()` natijasidagi nomlar. */
const TEXT_FIELDS = {
  eyebrow: 'eyebrow',
  title: 'title',
  subtitle: 'subtitle',
  text: 'text',
  note: 'note',
  button_label: 'buttonLabel',
  button2_label: 'button2Label',
}

/** Matnni maketdagidek qatorlarga ajratadi (sarlavhalar ko'p qatorli). */
export const toLines = (value) => String(value ?? '').split('\n')

/**
 * @param {string} key bo'lim kaliti, masalan `home.hero`
 * @param {Record<string, string>} fallbacks maydon → tarjima kaliti
 */
export function useSection(key, fallbacks = {}) {
  const store = useContentStore()
  const { t } = useI18n()

  return computed(() => {
    const data = store.get(key)

    const pick = (field, name) => {
      const value = data[field]
      if (value) return value
      const fallback = fallbacks[name] ?? fallbacks[field]
      return fallback ? t(fallback) : ''
    }

    const section = {
      items: data.items ?? [],
      image: data.image || null,
      image2: data.image2 || null,
      buttonUrl: data.button_url || '',
      button2Url: data.button2_url || '',
    }

    for (const [field, name] of Object.entries(TEXT_FIELDS)) {
      section[name] = pick(field, name)
    }
    section.titleLines = toLines(section.title)

    return section
  })
}

/**
 * Admin paneldagi elementlarni maketdagi kartochkalar bilan birlashtiradi.
 *
 * Panelda element qo'shilmagan bo'lsa — maketdagi ro'yxat qaytadi, ya'ni
 * bo'lim hech qachon bo'sh ko'rinmaydi. Rasm yoki ikonka to'ldirilmagan
 * bo'lsa, o'sha o'rindagi maket qiymati olinadi.
 *
 * @param {any[]} items admin paneldan kelgan elementlar
 * @param {any[]} fallback maketdagi kartochkalar (`{ id, title, description, icon }`)
 */
export function toCards(items, fallback = []) {
  if (!items?.length) return fallback

  return items.map((item, index) => {
    const preset = fallback[index] ?? {}
    return {
      id: item.id ?? preset.id ?? index,
      title: item.title || preset.title || '',
      description: item.text || preset.description || '',
      icon: item.icon_name || preset.icon || '',
      iconImage: item.icon || null,
      image: item.image || null,
      value: item.value || '',
    }
  })
}
