<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseLightbox from '@/components/base/BaseLightbox.vue'
import LeadSuccessPanel from '@/components/forms/LeadSuccessPanel.vue'
import AppToasts from '@/components/layout/AppToasts.vue'
import ScrollTopButton from '@/components/layout/ScrollTopButton.vue'
import { useSiteStore } from '@/stores/site'

const { t } = useI18n()
const site = useSiteStore()

onMounted(() => {
  document.documentElement.lang = site.language
  site.load()
})
</script>

<template>
  <a href="#main" class="skip-link">{{ t('header.skipToContent') }}</a>

  <RouterView v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>

  <LeadSuccessPanel />
  <BaseLightbox />
  <ScrollTopButton />
  <AppToasts />
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.18s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
