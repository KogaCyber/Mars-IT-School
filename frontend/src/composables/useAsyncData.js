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

  /** @param {boolean} silent spinner ko'rsatilmasin (fonda yangilash). */
  async function execute(silent = false) {
    if (!silent) isLoading.value = true
    error.value = null
    try {
      data.value = await loader()
    } catch (err) {
      error.value = normalizeError(err).detail
    } finally {
      if (!silent) isLoading.value = false
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
