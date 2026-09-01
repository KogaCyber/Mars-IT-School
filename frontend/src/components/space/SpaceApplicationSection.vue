<script setup>
/**
 * «Начните обучение с поддержкой SPACE» — SPACE sahifasining yakuniy bo'limi.
 *
 * Maket: chapda yorliq, yirik uch qatorli sarlavha va izoh; o'ngda shishasimon
 * ariza kartochkasi (pastki chiziqli maydonlar). Orqa fonda ko'k–to'q sariq nur.
 */
import { useI18n } from 'vue-i18n'

import glow from '@/assets/images/about-glow.webp'
import LeadForm from '@/components/forms/LeadForm.vue'

const { t } = useI18n()
</script>

<template>
  <section class="section bg-ink relative overflow-hidden">
    <!-- Fon nuri: kartochka ortidan chapga qarab so'nadi -->
    <img
      loading="lazy"
      decoding="async"
      :src="glow"
      alt=""
      aria-hidden="true"
      class="animate-glow pointer-events-none absolute top-1/2 left-1/2 w-[150%] max-w-none -translate-x-1/2 -translate-y-1/2 select-none lg:w-[95%]"
    />

    <div
      class="container-page relative grid items-center gap-[8%] lg:grid-cols-[1.15fr_1fr] lg:gap-[6%]"
    >
      <div>
        <p v-reveal class="eyebrow">{{ t('space.applicationEyebrow') }}</p>

        <h2 v-reveal class="title-hero font-wide mt-[5%] font-bold text-white">
          <span
            v-for="line in t('space.applicationTitle').split('\n')"
            :key="line"
            class="block"
          >
            {{ line }}
          </span>
          <span class="block">SPACE</span>
        </h2>

        <p v-reveal="{ delay: 120 }" class="mt-[7%] max-w-[46ch] leading-relaxed text-white/70">
          {{ t('space.applicationText') }}
        </p>
      </div>

      <!-- Ariza kartochkasi -->
      <div
        v-reveal="{ delay: 200 }"
        class="rounded-block mt-[6%] border border-white/10 bg-white/[0.06] p-[7%] backdrop-blur-xl lg:mt-0"
      >
        <h3 class="section-title font-wide font-bold text-white">
          <span class="text-brand">{{ t('forms.trialCardTitleAccent') }}</span>
          <br />
          {{ t('forms.trialCardTitle') }}
        </h3>

        <div class="mt-[8%]">
          <LeadForm
            source="space"
            variant="line"
            split-name
            :with-consent-note="false"
            :submit-label="t('forms.submitApplication')"
          />
        </div>
      </div>
    </div>
  </section>
</template>
