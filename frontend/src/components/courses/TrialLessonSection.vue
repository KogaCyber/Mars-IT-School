<script setup>
/**
 * «Бесплатное пробное занятие» — Figma: chapda yorliq, yirik uch qatorli
 * sarlavha va izoh; o'ngda shishasimon ariza kartochkasi. Orqa fonda
 * ko'k–to'q sariq nur.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import glow from '@/assets/images/about-glow.webp'
import LeadForm from '@/components/forms/LeadForm.vue'

const { t } = useI18n()

const props = defineProps({
  /** Ariza qayerdan kelgani — backendda statistika uchun. */
  source: { type: String, default: 'courses' },
  /** Sarlavha qatorlari — bo'sh qoldirilsa tarjimadan olinadi. */
  title: { type: Array, default: null },
  /** Sarlavha ostidagi izoh — bo'sh qoldirilsa tarjimadan olinadi. */
  description: { type: String, default: '' },
  /** Qaysi kurs qiziqtirgani (ixtiyoriy). */
  courseSlug: { type: String, default: null },
  /** Alohida sahifada sarlavha `h1` bo'lishi kerak. */
  headingLevel: { type: String, default: 'h2' },
})

const titleLines = computed(() => props.title || t('forms.trialTitle').split('\n'))
const descriptionText = computed(() => props.description || t('forms.trialDescription'))
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
      class="section-glow animate-glow pointer-events-none absolute top-1/2 left-1/2 w-[150%] max-w-none -translate-x-1/2 -translate-y-1/2 select-none lg:w-[95%]"
    />

    <div
      class="container-page relative grid items-center gap-[8%] lg:grid-cols-[1.15fr_1fr] lg:gap-[6%]"
    >
      <div>
        <p v-reveal class="eyebrow">{{ t('forms.trialEyebrow') }}</p>

        <component
          :is="headingLevel"
          v-reveal
          class="title-hero font-wide mt-[5%] font-bold text-white"
        >
          <span v-for="line in titleLines" :key="line" class="block">{{ line }}</span>
        </component>

        <p v-reveal="{ delay: 120 }" class="mt-[7%] max-w-[46ch] leading-relaxed text-white/70">
          {{ descriptionText }}
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
            :source="source"
            :course-slug="courseSlug"
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

<style scoped>
/* Nur rasmi bo'lim chetida kesilib, keskin qirra hosil qilmasin */
.section-glow {
  mask-image:
    linear-gradient(to bottom, transparent 0, #000 12%, #000 88%, transparent 100%),
    linear-gradient(to right, transparent 0, #000 8%, #000 92%, transparent 100%);
  mask-composite: intersect;
  -webkit-mask-composite: source-in;
}
</style>
