<script setup>
import { useI18n } from 'vue-i18n'

import BaseButton from '@/components/base/BaseButton.vue'
import { useSeo } from '@/composables/useSeo'

const { t } = useI18n()

useSeo(() => ({
  title: t('pages.notFoundTitle'),
  description: t('pages.notFoundDescription'),
  noindex: true,
}))
</script>

<template>
  <section class="section bg-ink">
    <div class="container-page flex flex-col items-center py-20 text-center">
      <p class="font-wide text-[clamp(4rem,8.3vw,10rem)] leading-none font-bold text-brand">404</p>
      <h1 class="title-block mt-6 font-wide font-bold text-white">{{ t('pages.notFoundHeading') }}</h1>
      <p class="mt-4 max-w-md text-base text-white/70">
        {{ t('pages.notFoundText') }}
      </p>

      <BaseButton :to="{ name: 'home' }" size="lg" class="mt-10 font-wide font-bold">
        {{ t('pages.notFoundButton') }}
      </BaseButton>
    </div>
  </section>
</template>
