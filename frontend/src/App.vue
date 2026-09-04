<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseLightbox from '@/components/base/BaseLightbox.vue'
import BaseVideoModal from '@/components/base/BaseVideoModal.vue'
import LeadSuccessPanel from '@/components/forms/LeadSuccessPanel.vue'
import AppToasts from '@/components/layout/AppToasts.vue'
import ScrollTopButton from '@/components/layout/ScrollTopButton.vue'
import { setLanguage as persistLanguage } from '@/i18n/language'
import { useLiveStore } from '@/stores/live'
import { useSiteStore } from '@/stores/site'

const { t } = useI18n()
const site = useSiteStore()
const live = useLiveStore()

onMounted(() => {
  document.documentElement.lang = site.language
  // `?lang=` bilan kelgan tashrifchining tanlovi saqlanadi — keyingi
  // sahifalarda (parametrsiz havolalarda) ham o'sha til qoladi.
  persistLanguage(site.language)
  site.load()

  // Admin paneldagi o'zgarishlar sahifa yangilanmasdan ko'rinishi uchun
  // kontent versiyasi kuzatib boriladi (stores/live.js).
  live.start()
  live.subscribe(() => site.refresh())
})
</script>

<template>
  <a href="#main" class="skip-link">{{ t('header.skipToContent') }}</a>

  <RouterView />

  <LeadSuccessPanel />
  <BaseLightbox />
  <BaseVideoModal />
  <ScrollTopButton />
  <AppToasts />
</template>
