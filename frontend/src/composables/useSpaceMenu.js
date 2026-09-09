/**
 * SPACE platformasi maketining chap menyusi — admin paneldan boshqariladi.
 *
 * Admin panel: Bosh sahifa → «SPACE maketi — chap menyu va ekran rasmlari».
 * Har bir element = bitta tugma:
 *   sarlavha   → tugma matni
 *   ikonka nomi/rasmi → tugma yonidagi belgi
 *   rasm       → tugma bosilganda o'ngda ko'rsatiladigan ekran rasmi
 *
 * Rasm yuklanmagan tugma uchun maketdagi jonli ko'rinish (`SPACE_VIEWS`)
 * chiziladi — shuning uchun panel bo'sh bo'lsa ham sayt hozirgidek ishlaydi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { useSection } from '@/composables/useSection'
import { SPACE_MENU } from '@/data/spacePlatform'

/** Menyu ikonkalari — sodda chiziqli belgilar (admin panelda nomi bilan tanlanadi). */
export const SPACE_MENU_ICONS = {
  book: 'M4 5.5A1.5 1.5 0 0 1 5.5 4H10v12H5.5A1.5 1.5 0 0 1 4 14.5v-9ZM10 4h4.5A1.5 1.5 0 0 1 16 5.5v9a1.5 1.5 0 0 1-1.5 1.5H10',
  play: 'M4 6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Zm4 2.5v3l3-1.5-3-1.5Z',
  star: 'm10 3.5 2 4.2 4.5.6-3.3 3.2.8 4.5-4-2.2-4 2.2.8-4.5L3.5 8.3l4.5-.6 2-4.2Z',
  trophy: 'M6 4h8v3a4 4 0 0 1-8 0V4Zm0 1H4v1a2 2 0 0 0 2 2m8-3h2v1a2 2 0 0 1-2 2m-4 4v3m-2.5 0h5',
  chat: 'M4 5.5A1.5 1.5 0 0 1 5.5 4h9A1.5 1.5 0 0 1 16 5.5v6A1.5 1.5 0 0 1 14.5 13H8l-4 3v-3.5A1.5 1.5 0 0 1 4 11.5v-6Z',
  bag: 'M5 6h10l-.8 9.2a1.5 1.5 0 0 1-1.5 1.3H7.3a1.5 1.5 0 0 1-1.5-1.3L5 6Zm2.5 0V5a2.5 2.5 0 0 1 5 0v1',
}

const DEFAULT_ICON = 'book'

/**
 * Maketning menyu tugmalari.
 *
 * @returns {import('vue').ComputedRef<Array<{
 *   id: string, label: string, icon: string, iconImage: string|null,
 *   image: string|null, viewId: string|null,
 * }>>}
 */
export function useSpaceMenu() {
  const { t } = useI18n()
  const section = useSection('home.platform')

  return computed(() => {
    const items = section.value.items

    // Panelda element yo'q — maketdagi olti bo'lim.
    if (!items.length) {
      return SPACE_MENU.map((item) => ({
        id: item.id,
        label: t(`spaceMenu.${item.id}`),
        icon: item.icon,
        iconImage: null,
        image: null,
        viewId: item.id,
      }))
    }

    return items.map((item, index) => {
      // Shu o'rindagi maket bo'limi: matn yoki ikonka to'ldirilmagan bo'lsa
      // undan olinadi, rasm yuklanmagan bo'lsa esa uning jonli ko'rinishi.
      const preset = SPACE_MENU[index]
      const image = item.image || null

      return {
        id: `item-${item.id ?? index}`,
        label: item.title || (preset ? t(`spaceMenu.${preset.id}`) : ''),
        icon: SPACE_MENU_ICONS[item.icon_name] ? item.icon_name : (preset?.icon ?? DEFAULT_ICON),
        iconImage: item.icon || null,
        image,
        viewId: image ? null : (preset?.id ?? null),
      }
    })
  })
}
