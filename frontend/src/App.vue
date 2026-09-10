<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseLightbox from '@/components/base/BaseLightbox.vue'
import BaseVideoModal from '@/components/base/BaseVideoModal.vue'
import LeadSuccessPanel from '@/components/forms/LeadSuccessPanel.vue'
import AiAssistant from '@/components/layout/AiAssistant.vue'
import AppToasts from '@/components/layout/AppToasts.vue'
import ScrollTopButton from '@/components/layout/ScrollTopButton.vue'
import { setLanguage as persistLanguage } from '@/i18n/language'
import { useContentStore } from '@/stores/content'
import { useLiveStore } from '@/stores/live'
import { useSiteStore } from '@/stores/site'
import { clearAssistantData } from '@/utils/assistantData'

const { t } = useI18n()
const site = useSiteStore()
const content = useContentStore()
const live = useLiveStore()

onMounted(() => {
  document.documentElement.lang = site.language
  // `?lang=` bilan kelgan tashrifchining tanlovi saqlanadi — keyingi
  // sahifalarda (parametrsiz havolalarda) ham o'sha til qoladi.
  persistLanguage(site.language)
  site.load()
  // Sahifa bo'limlarining matni va rasmlari — admin paneldan (stores/content.js).
  content.load()

  // Admin paneldagi o'zgarishlar sahifa yangilanmasdan ko'rinishi uchun
  // kontent versiyasi kuzatib boriladi (stores/live.js).
  live.start()
  live.subscribe(() => {
    site.refresh()
    content.load({ force: true })
    // AI yordamchisi ham yangi ma'lumot bilan javob bersin.
    clearAssistantData()
  })
})
</script>

<template>
  <a href="#main" class="skip-link">{{ t('header.skipToContent') }}</a>

  <RouterView />

  <LeadSuccessPanel />
  <BaseLightbox />
  <BaseVideoModal />
  <ScrollTopButton />
  <AiAssistant />
  <AppToasts />
</template>
