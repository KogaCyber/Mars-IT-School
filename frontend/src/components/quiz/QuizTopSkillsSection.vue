<script setup>
/**
 * «3 самые сильные сферы» — eng yuqori foizli uchta ko'nikma.
 *
 * Har bir kartochkada: yirik shaffof foiz, o'rin belgisi va halqa diagramma
 * (to'ldirilgan qismi foizga teng, markazida ko'nikma ikonkasi).
 */
import { computed } from 'vue'
import { useSection } from '@/composables/useSection'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Natija sahifasi sarlavhalari admin paneldan («Test» sahifasi bo'limlari → «Natija»).
const result = useSection('quiz.result', {
  title: 'quiz.resultTitle',
  eyebrow: 'quiz.skillsEyebrow',
  subtitle: 'quiz.skillsSubtitle',
  text: 'quiz.topSkillsTitle',
})

const props = defineProps({
  /** `[{ code, title, percent }]` — foiz bo'yicha kamayish tartibida. */
  skills: { type: Array, default: () => [] },
})

/** Halqa uzunligi: r = 52 → 2πr. */
const CIRCUMFERENCE = 2 * Math.PI * 52

/** Ko'nikma ikonkalari — chiziqli belgilar. */
const ICONS = {
  logic:
    'M8 6.5h3.2a2 2 0 0 1 2 2v7a2 2 0 0 0 2 2H18M8 6.5 6 4.5M8 6.5l-2 2M18 15.5l2-2M18 15.5l2 2M13.2 12H18',
  math: 'M6 8.5h5M8.5 6v5M14 8.5h4M14 15.5h4M14 13h4M6.6 14l3.4 3.4M10 14l-3.4 3.4',
  accuracy:
    'M12 4.5v3M12 16.5v3M4.5 12h3M16.5 12h3M12 8.4a3.6 3.6 0 1 1 0 7.2 3.6 3.6 0 0 1 0-7.2Z',
  patience: 'M12 4.2a7.8 7.8 0 1 1 0 15.6 7.8 7.8 0 0 1 0-15.6ZM12 8v4.3l2.8 1.7M9 2.8h6',
  creativity:
    'M12 4.2a5.6 5.6 0 0 1 3.4 10.1c-.6.5-.9 1.1-.9 1.8v.4h-5v-.4c0-.7-.3-1.3-.9-1.8A5.6 5.6 0 0 1 12 4.2ZM10 19.2h4M10.6 21h2.8',
  visual:
    'M2.8 12S6.4 6.4 12 6.4 21.2 12 21.2 12 17.6 17.6 12 17.6 2.8 12 2.8 12Zm9.2-2.6a2.6 2.6 0 1 1 0 5.2 2.6 2.6 0 0 1 0-5.2Z',
  communication:
    'M5.5 6.5h13a1.6 1.6 0 0 1 1.6 1.6v6.6a1.6 1.6 0 0 1-1.6 1.6H12l-4.6 3.2v-3.2H5.5a1.6 1.6 0 0 1-1.6-1.6V8.1a1.6 1.6 0 0 1 1.6-1.6Z',
  social:
    'M9 11a2.9 2.9 0 1 0 0-5.8A2.9 2.9 0 0 0 9 11Zm7 0a2.4 2.4 0 1 0 0-4.8 2.4 2.4 0 0 0 0 4.8ZM3.6 18.6c0-2.6 2.4-4.4 5.4-4.4s5.4 1.8 5.4 4.4M16.4 14.4c2.3.2 4 1.8 4 4.2',
}

const cards = computed(() =>
  props.skills.slice(0, 3).map((skill, index) => ({
    ...skill,
    place: t('quiz.place', { n: index + 1 }),
    /** Halqaning to'ldirilgan qismi. */
    dash: `${(CIRCUMFERENCE * skill.percent) / 100} ${CIRCUMFERENCE}`,
  })),
)
</script>

<template>
  <section v-if="cards.length" v-reveal class="bg-ink pb-[var(--spacing-section)]">
    <div class="container-page">
      <div class="bg-surface rounded-[2.5rem] p-7 sm:p-10 lg:p-14">
        <!-- Sarlavha qatori -->
        <header class="flex items-start gap-5">
          <span
            class="grid size-12 shrink-0 place-items-center rounded-2xl border border-white/20 text-white"
            aria-hidden="true"
          >
            <svg class="size-6" viewBox="0 0 24 24" fill="none">
              <path
                d="M7.5 4.5h9v4.2a4.5 4.5 0 0 1-9 0V4.5ZM7.5 6H5.2v1.1A2.8 2.8 0 0 0 7.9 9.9M16.5 6h2.3v1.1a2.8 2.8 0 0 1-2.7 2.8M12 13.2V16M9 19.5h6M10 16h4"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>

          <div>
            <h2 class="text-brand font-wide text-[1.05rem] font-bold">{{ result.text }}</h2>
            <p class="font-wide mt-1.5 text-[1.05rem] leading-snug font-bold text-white">
              {{ t('quiz.topSkillsSubtitle') }}
            </p>
          </div>
        </header>

        <!-- Uchta kartochka -->
        <ol class="mt-10 grid gap-5 md:grid-cols-3">
          <li
            v-for="card in cards"
            :key="card.code"
            class="bg-ink flex h-full flex-col justify-between rounded-[1.75rem] p-7 lg:p-8"
          >
            <div class="flex items-center justify-between gap-5">
              <div>
                <p
                  class="font-wide text-[clamp(2rem,3.4vw,2.75rem)] leading-none font-bold text-white/20"
                >
                  {{ card.percent }}%
                </p>

                <span
                  class="mt-6 inline-flex rounded-pill bg-white/6 px-5 py-2.5 font-medium text-white"
                >
                  {{ card.place }}
                </span>
              </div>

              <!-- Halqa diagramma: to'ldirilgan qismi foizga teng, markazida ikonka -->
              <div class="relative size-28 shrink-0">
                <svg class="size-full -rotate-90" viewBox="0 0 120 120" aria-hidden="true">
                  <defs>
                    <linearGradient :id="`ring-${card.code}`" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stop-color="#e2451f" />
                      <stop offset="100%" stop-color="#3b2f7a" />
                    </linearGradient>
                  </defs>

                  <circle cx="60" cy="60" r="52" fill="none" stroke="#ffffff14" stroke-width="8" />
                  <circle
                    cx="60"
                    cy="60"
                    r="52"
                    fill="none"
                    :stroke="`url(#ring-${card.code})`"
                    stroke-width="8"
                    stroke-linecap="round"
                    :stroke-dasharray="card.dash"
                  />
                </svg>

                <span class="absolute inset-0 grid place-items-center" aria-hidden="true">
                  <span
                    class="grid size-14 place-items-center rounded-full bg-white/6 text-white/40"
                  >
                    <svg class="size-6" viewBox="0 0 24 24" fill="none">
                      <path
                        :d="ICONS[card.code] || ICONS.logic"
                        stroke="currentColor"
                        stroke-width="1.4"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>
                </span>
              </div>
            </div>

            <p class="font-wide mt-8 font-bold text-white">{{ card.title }}</p>
          </li>
        </ol>
      </div>
    </div>
  </section>
</template>
