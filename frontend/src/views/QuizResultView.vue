<script setup>
/**
 * «Результаты теста» sahifasi — hozircha faqat bosh qismi.
 *
 * Maket: tepada yo'l yorliqlari va yirik «Ваш результат готов!» sarlavhasi,
 * ostida bitta katta to'q kartochka:
 *   1) ogohlantirish qatori (doiradagi «!», to'q sariq yorliq va xulosa),
 *   2) izoh matni,
 *   3) ikkita bosqich kartochkasi — o'ng chetida yirik «01» / «02» raqami
 *      va uning ortida rangli nur (birinchisi issiq, ikkinchisi sovuq),
 *   4) pastda uchta yorliq: bosqichlar va yakuniy natija.
 *
 * Matnlar `data/quizOutcomes.js` dan olinadi — natija kodiga (`backend` yoki
 * `frontend`) qarab tanlanadi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { fetchQuizResult } from '@/api/quiz'
import { fetchStatistics } from '@/api/site'
import BaseBreadcrumbs from '@/components/base/BaseBreadcrumbs.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import QuizOutcomeMatch from '@/components/quiz/QuizOutcomeMatch.vue'
import QuizOutcomePath from '@/components/quiz/QuizOutcomePath.vue'
import QuizCtaSection from '@/components/quiz/QuizCtaSection.vue'
import QuizOutcomePlan from '@/components/quiz/QuizOutcomePlan.vue'
import QuizOutcomeProfile from '@/components/quiz/QuizOutcomeProfile.vue'
import QuizSkillsSection from '@/components/quiz/QuizSkillsSection.vue'
import QuizSummarySection from '@/components/quiz/QuizSummarySection.vue'
import QuizTopSkillsSection from '@/components/quiz/QuizTopSkillsSection.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useSeo } from '@/composables/useSeo'
import { useQuizContent } from '@/utils/quizContent'

const { t } = useI18n()

const props = defineProps({
  /** Natijaning maxfiy kaliti — manzildan keladi (`/test/rezultat/:token`). */
  token: { type: String, required: true },
})

const token = computed(() => props.token)
const {
  data: result,
  isLoading,
  error,
} = useAsyncData(() => fetchQuizResult(token.value), null, {
  watchSource: token,
})

const outcome = computed(() => result.value?.outcome || null)
/** Ko'nikmalar tahlili — backenddan foiz bo'yicha tartiblangan holda keladi. */
const skills = computed(() => result.value?.skills || [])

/** «Приведите ребёнка в MARS IT» blokidagi raqamlar — admin paneldan. */
const { data: statistics } = useAsyncData(fetchStatistics, [])

/**
 * Sahifa matnlari: yo'nalishga bog'liq o'zgarmas qismlar + shu topshiriqning
 * foizlari va ko'nikmalaridan yig'ilgan dinamik matnlar.
 */
const details = useQuizContent(
  computed(() => ({
    outcome: outcome.value,
    matches: result.value?.matches || [],
    skills: skills.value,
  })),
)

useSeo(() => ({
  title: t('quiz.resultSeoTitle'),
  description: details.value.headline,
  // Natija har bir foydalanuvchi uchun shaxsiy — qidiruvga chiqishi shart emas.
  noindex: true,
}))
</script>

<template>
  <BaseSpinner v-if="isLoading" :label="t('quiz.resultLoading')" />

  <div v-else-if="error || !result" class="section container-page">
    <BaseEmptyState :title="t('quiz.resultNotFound')" :description="error || ''">
      <BaseButton :to="{ name: 'quiz' }">{{ t('quiz.takeQuiz') }}</BaseButton>
    </BaseEmptyState>
  </div>

  <template v-else>
    <section class="bg-ink pt-[3%] pb-[var(--spacing-block)]">
      <div class="container-page">
        <BaseBreadcrumbs
          :items="[
            { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
            { label: t('nav.quiz'), to: { name: 'quiz' } },
            { label: t('quiz.breadcrumbResults') },
          ]"
        />

        <h1 v-reveal class="title-result font-wide mt-[4%] font-bold text-white">
          {{ t('quiz.resultTitle') }}
        </h1>

        <!-- Katta kartochka -->
        <div
          v-reveal="{ delay: 120 }"
          class="bg-surface mt-[5%] rounded-[2.5rem] p-7 sm:p-10 lg:p-14"
        >
          <!-- 1. Ogohlantirish qatori -->
          <div class="flex items-start gap-5">
            <span
              class="grid size-12 shrink-0 place-items-center rounded-full border border-white/20 text-white"
              aria-hidden="true"
            >
              <svg class="size-6" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 7.5v6M12 16.8h.01"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>
            </span>

            <div>
              <p class="text-brand font-wide text-[1.05rem] font-bold">{{ details.label }}</p>
              <p class="font-wide mt-1.5 text-[1.05rem] leading-snug font-bold text-white">
                {{ details.headline }}
              </p>
            </div>
          </div>

          <!-- 2. Izoh -->
          <p class="mt-7 max-w-[92ch] leading-relaxed text-white/40">{{ details.description }}</p>

          <!-- 3. Bosqich kartochkalari -->
          <ul class="mt-8 grid gap-5 lg:grid-cols-2">
            <li
              v-for="stepItem in details.steps"
              :key="stepItem.number"
              class="bg-ink relative overflow-hidden rounded-[1.75rem] p-7 lg:p-8"
            >
              <!-- Raqam ortidagi rangli nur -->
              <span
                class="pointer-events-none absolute top-1/2 right-0 h-[135%] w-[52%] -translate-y-1/2 rounded-full"
                :class="stepItem.tone === 'brand' ? 'glow-brand' : 'glow-violet'"
                aria-hidden="true"
              />

              <span
                class="font-wide pointer-events-none absolute top-1/2 right-6 -translate-y-1/2 leading-none font-bold text-white/10 select-none"
                style="font-size: clamp(3.5rem, 7vw, 6rem)"
                aria-hidden="true"
              >
                {{ stepItem.number }}
              </span>

              <div class="relative max-w-[34ch]">
                <h2 class="font-wide text-[1.05rem] leading-snug font-bold text-white">
                  {{ stepItem.title }}
                </h2>
                <p class="mt-4 leading-relaxed text-white/60">{{ stepItem.description }}</p>
              </div>
            </li>
          </ul>

          <!-- 4. Yakuniy yorliqlar -->
          <ul class="mt-6 flex flex-wrap gap-3">
            <li
              v-for="chip in details.chips"
              :key="chip.value"
              class="bg-ink font-wide rounded-pill px-6 py-3.5 font-bold"
            >
              <span :class="chip.accent ? 'text-brand' : 'text-white/35'">{{ chip.label }} -</span>
              <span class="text-white"> {{ chip.value }}</span>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <QuizOutcomeProfile :profile="details.profile" />

    <QuizOutcomeMatch :matches="result.matches || []" :active-code="outcome?.code || ''" />

    <QuizOutcomePath :path="details.path" />

    <QuizSkillsSection :skills="skills" />

    <QuizTopSkillsSection :skills="skills" />

    <QuizOutcomePlan :plan="details.plan" />

    <QuizCtaSection :stats="statistics" />

    <QuizSummarySection
      :outcome="outcome"
      :matches="result.matches || []"
      :skills="skills"
      :note="details.summaryNote"
      :growth-skill="details.growthSkill"
    />
  </template>
</template>

<style scoped>
/* Maketda sarlavha sahifa sarlavhalaridan yirikroq */
.title-result {
  font-size: clamp(2.25rem, 5.6vw, 6rem);
  line-height: 1.03;
}

/* Raqam ortidagi nur: birinchi kartochkada issiq, ikkinchisida sovuq */
.glow-brand {
  background: radial-gradient(closest-side, rgba(233, 73, 33, 0.32), transparent 78%);
}

.glow-violet {
  background: radial-gradient(closest-side, rgba(84, 92, 214, 0.34), transparent 78%);
}
</style>
