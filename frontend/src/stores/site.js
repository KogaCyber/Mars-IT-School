/** Sayt bo'yicha umumiy ma'lumot (kontaktlar, til) — bir marta yuklanadi. */
import { defineStore } from 'pinia'
import { ref } from 'vue'

import { fetchSiteSettings } from '@/api/site'
import { setI18nLanguage } from '@/i18n'
import { getLanguage, setLanguage as persistLanguage } from '@/i18n/language'
import { useContentStore } from '@/stores/content'

const EMPTY_SETTINGS = {
  phone: '',
  extra_phone: '',
  email: '',
  telegram_url: '',
  instagram_url: '',
  youtube_url: '',
  facebook_url: '',
  space_app_ios_url: '',
  space_app_android_url: '',
  privacy_policy_url: '',
  promo_video_url: '',
  promo_video: '',
  promo_cover: '',
}

export const useSiteStore = defineStore('site', () => {
  const settings = ref({ ...EMPTY_SETTINGS })
  const isLoaded = ref(false)
  const language = ref(getLanguage())

  async function load({ force = false } = {}) {
    if (isLoaded.value && !force) return
    try {
      settings.value = await fetchSiteSettings()
    } catch {
      // Kontaktlar yuklanmasa ham sayt ishlashda davom etadi.
      settings.value = { ...EMPTY_SETTINGS }
    } finally {
      isLoaded.value = true
    }
  }

  /** Admin panelda sozlamalar o'zgarganda — jimgina qayta yuklash. */
  async function refresh() {
    await load({ force: true })
  }

  /** Tilni almashtirib, kontentni qayta yuklaydi. */
  async function changeLanguage(next) {
    if (next === language.value) return
    persistLanguage(next)
    language.value = next
    setI18nLanguage(next)
    isLoaded.value = false
    // Sahifa bo'limlari ham tarjimalanadi — yangi tilda qayta olinadi.
    await Promise.all([load(), useContentStore().load({ force: true })])
  }

  return { settings, isLoaded, language, load, refresh, changeLanguage }
})
