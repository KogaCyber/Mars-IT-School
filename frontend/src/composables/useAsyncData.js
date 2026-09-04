/** Ma'lumot yuklashning takrorlanuvchi mantiqini (loading / error / retry) bir joyga yig'adi. */
import { getCurrentScope, onScopeDispose, ref, shallowRef, watch } from 'vue'

import { normalizeError } from '@/api/client'
import { i18n } from '@/i18n'
import { useLiveStore } from '@/stores/live'

/**
 * Backend kontenti ham tarjimalanadi (`Accept-Language` sarlavhasi orqali),
 * shuning uchun til almashganda ma'lumot avtomatik qayta yuklanadi — sahifani
 * yangilash shart emas. Buni `reloadOnLanguageChange: false` bilan o'chirish
 * mumkin (masalan javob tilga bog'liq bo'lmaganda).
 *
 * Xuddi shunday: admin panelda kontent o'zgarsa, sahifa yangilanmasa ham
 * ma'lumot o'zi qayta yuklanadi (`stores/live.js`). Bunday yangilanish
 * "jimgina" bo'ladi — spinner ko'rsatilmaydi, ekrandagi kontent joyida
 * turaveradi va yangisi kelganda almashadi. Buni `reloadOnContentChange:
 * false` bilan o'chirish mumkin (masalan javob bir martalik bo'lsa).
 *
 * @param {() => Promise<any>} loader ma'lumotni yuklovchi funksiya
 * @param {any} initialValue boshlang'ich qiymat
 * @param {{immediate?: boolean, watchSource?: any, reloadOnLanguageChange?: boolean,
 *          reloadOnContentChange?: boolean}} options
 */
export function useAsyncData(loader, initialValue, options = {}) {
  const {
    immediate = true,
    watchSource,
    reloadOnLanguageChange = true,
    reloadOnContentChange = true,
  } = options

  const data = shallowRef(initialValue)
  const error = ref(null)
  const isLoading = ref(false)

  /**
   * Oxirgi so'rovning tartib raqami.
   *
   * Bir necha yuklash ustma-ust ketishi mumkin: til almashdi, admin panelda
   * kontent o'zgardi, filtr bosildi. Javoblar esa yuborilgan tartibda
   * qaytmaydi — sekinroq ESKI javob keyinroq kelib, yangisining ustiga
   * yozilib qolardi (til almashtirilgach eski tildagi matn qaytib qolishi —
   * aynan shundan). Faqat eng oxirgi so'rovning javobi qabul qilinadi.
   */
  let requestId = 0
  /** Spinner ko'rsatayotgan so'rovlar soni — oxirgisi tugagach spinner o'chadi. */
  let visibleRequests = 0

  /** @param {boolean} silent spinner ko'rsatilmasin (fonda yangilash). */
  async function execute(silent = false) {
    const id = ++requestId
    if (!silent) {
      visibleRequests += 1
      isLoading.value = true
    }
    error.value = null
    try {
      const result = await loader()
      if (id !== requestId) return
      data.value = result
    } catch (err) {
      if (id !== requestId) return
      error.value = normalizeError(err).detail
    } finally {
      if (!silent) {
        visibleRequests -= 1
        if (visibleRequests === 0) isLoading.value = false
      }
    }
  }

  if (watchSource) {
    watch(watchSource, () => execute(), { deep: true })
  }
  // Til almashdi — backenddan kelgan matnlar ham yangi tilda kelishi kerak.
  if (reloadOnLanguageChange) {
    watch(i18n.global.locale, () => execute())
  }
  // Admin panelda kontent o'zgardi — ekrandagi ma'lumot ham yangilanadi.
  if (reloadOnContentChange && getCurrentScope()) {
    const live = useLiveStore()
    onScopeDispose(live.subscribe(() => execute(true)))
  }
  if (immediate) execute()

  return { data, error, isLoading, execute }
}
