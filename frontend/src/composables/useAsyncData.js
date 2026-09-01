/** Ma'lumot yuklashning takrorlanuvchi mantiqini (loading / error / retry) bir joyga yig'adi. */
import { ref, shallowRef, watch } from 'vue'

import { normalizeError } from '@/api/client'
import { i18n } from '@/i18n'

/**
 * Backend kontenti ham tarjimalanadi (`Accept-Language` sarlavhasi orqali),
 * shuning uchun til almashganda ma'lumot avtomatik qayta yuklanadi — sahifani
 * yangilash shart emas. Buni `reloadOnLanguageChange: false` bilan o'chirish
 * mumkin (masalan javob tilga bog'liq bo'lmaganda).
 *
 * @param {() => Promise<any>} loader ma'lumotni yuklovchi funksiya
 * @param {any} initialValue boshlang'ich qiymat
 * @param {{immediate?: boolean, watchSource?: any, reloadOnLanguageChange?: boolean}} options
 */
export function useAsyncData(loader, initialValue, options = {}) {
  const { immediate = true, watchSource, reloadOnLanguageChange = true } = options

  const data = shallowRef(initialValue)
  const error = ref(null)
  const isLoading = ref(false)

  async function execute() {
    isLoading.value = true
    error.value = null
    try {
      data.value = await loader()
    } catch (err) {
      error.value = normalizeError(err).detail
    } finally {
      isLoading.value = false
    }
  }

  if (watchSource) {
    watch(watchSource, () => execute(), { deep: true })
  }
  // Til almashdi — backenddan kelgan matnlar ham yangi tilda kelishi kerak.
  if (reloadOnLanguageChange) {
    watch(i18n.global.locale, () => execute())
  }
  if (immediate) execute()

  return { data, error, isLoading, execute }
}
