<script setup>
/**
 * «Анализ способностей» — testda o'lchangan sakkizta ko'nikma.
 *
 * Foizlar backenddan keladi (`/quiz-results/<id>/` → `skills`): har bir javob
 * varianti bitta ko'nikmani ko'rsatadi, foiz — shu ko'nikma taklif qilingan
 * savollarda to'plangan ballning maksimumga nisbati.
 *
 * Maket: chapda ko'nikma nomi, o'ngda foiz kapsulasi, ostida chiziq. Ikki
 * ustunli to'r — sakkizta qator ekranga bir ko'rinishda sig'adi.
 */
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps({
  /** `[{ code, title, percent }]` — foiz bo'yicha kamayish tartibida. */
  skills: { type: Array, default: () => [] },
})
</script>

<template>
  <section v-if="skills.length" v-reveal class="bg-ink pb-[var(--spacing-block)]">
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
                d="M5.5 18.5V5.5M5.5 18.5h13M8.5 15.5v-3M12 15.5V9.8M15.5 15.5v-4M13.8 7.2h4v4"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="m11 11 3.2-3.2"
                stroke="currentColor"
                stroke-width="1.4"
                stroke-linecap="round"
              />
            </svg>
          </span>

          <div>
            <h2 class="text-brand font-wide text-[1.05rem] font-bold">{{ t('quiz.skillsEyebrow') }}</h2>
            <p class="font-wide mt-1.5 text-[1.05rem] leading-snug font-bold text-white">
              {{ t('quiz.skillsSubtitle') }}
            </p>
          </div>
        </header>

        <!-- Ko'nikmalar to'ri -->
        <ul class="mt-10 grid gap-x-14 gap-y-8 lg:grid-cols-2">
          <li v-for="skill in skills" :key="skill.code">
            <div class="flex items-center justify-between gap-4">
              <p class="font-wide font-bold text-white">{{ skill.title }}</p>

              <span
                class="font-wide shrink-0 rounded-pill px-4 py-1.5 text-sm font-bold text-white"
                style="background: linear-gradient(120deg, #e2451f 0%, #c0392b 100%)"
              >
                {{ skill.percent }}%
              </span>
            </div>

            <div class="mt-3 h-2 overflow-hidden rounded-pill bg-white/8">
              <div
                class="h-full rounded-pill transition-all duration-700"
                :style="{
                  width: `${skill.percent}%`,
                  background: 'linear-gradient(90deg, #e2451f 0%, #a63a5a 60%, #3b2f7a 100%)',
                }"
              />
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>
