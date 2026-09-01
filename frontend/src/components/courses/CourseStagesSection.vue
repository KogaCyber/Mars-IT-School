<script setup>
/**
 * «Программа» bo'limi — Figma: yorliq, yirik sarlavha, chapda izoh va
 * o'ngda qisqa xulosa; ostida bosqichlar akkordeoni.
 *
 * Bir vaqtda bitta bosqich ochiq turadi (birinchisi boshlang'ich holatda).
 * Ochilish `grid-template-rows: 0fr → 1fr` orqali silliq animatsiyalanadi —
 * balandlikni JS bilan o'lchash shart emas.
 */
import { computed, ref, useId } from 'vue'
import { useI18n } from 'vue-i18n'

import checkBadge from '@/assets/images/Layer-02 1.webp'
import { TECH } from '@/data/directions'

const { t } = useI18n()

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  /** O'ng tomondagi qisqa xulosa yorlig'i. */
  summary: { type: String, default: '' },
  /** Bo'sh qoldirilsa — «Dastur» tarjimasi ishlatiladi. */
  eyebrow: { type: String, default: '' },
  /** `[{ number, title, duration, description, topics, tools, result }]`. */
  stages: { type: Array, required: true },
  topicsLabel: { type: String, default: '' },
  toolsLabel: { type: String, default: '' },
})

const eyebrowText = computed(() => props.eyebrow || t('courses.programEyebrow'))
const topicsLabelText = computed(() => props.topicsLabel || t('courses.topicsLabel'))
const toolsLabelText = computed(() => props.toolsLabel || t('courses.toolsLabel'))

const uid = useId()
const openIndex = ref(0)

function toggle(index) {
  openIndex.value = openIndex.value === index ? null : index
}

/** Noma'lum kalitlar tushib qolsin — maket buzilmaydi. */
function badgesOf(stage) {
  return (stage.tools || []).map((key) => TECH[key]).filter(Boolean)
}
</script>

<template>
  <section class="section bg-ink scroll-mt-[7rem]">
    <div class="container-page">
      <p v-reveal class="eyebrow">{{ eyebrowText }}</p>

      <h2 v-reveal class="title-hero font-wide mt-[2.5%] font-bold text-white">{{ title }}</h2>

      <div
        v-reveal="{ delay: 120 }"
        class="mt-[3.5%] flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between"
      >
        <p v-if="description" class="max-w-[46ch] leading-relaxed text-white/60">
          {{ description }}
        </p>

        <span
          v-if="summary"
          class="bg-surface rounded-pill text-small shrink-0 self-start px-[1.35em] py-[0.75em] font-bold text-white sm:self-auto"
        >
          {{ summary }}
        </span>
      </div>

      <!-- Bosqichlar -->
      <ul class="mt-[var(--spacing-block)] flex flex-col gap-[var(--spacing-gutter)]">
        <li
          v-for="(stage, index) in stages"
          :key="stage.number"
          v-reveal
          class="rounded-block bg-surface overflow-hidden transition-colors"
          :class="openIndex === index ? 'bg-surface' : 'hover:bg-surface-2'"
        >
          <h3>
            <button
              type="button"
              class="flex w-full cursor-pointer items-start gap-[4%] p-[1.75rem] text-left md:p-[2.5rem]"
              :id="`${uid}-button-${index}`"
              :aria-expanded="openIndex === index"
              :aria-controls="`${uid}-panel-${index}`"
              @click="toggle(index)"
            >
              <span
                class="font-wide hidden w-[3.4em] shrink-0 text-[2.6rem] leading-none font-bold text-white/10 md:block lg:text-[3.4rem]"
                aria-hidden="true"
              >
                {{ stage.number }}
              </span>

              <span class="min-w-0 flex-1">
                <span class="flex flex-wrap items-center gap-x-4 gap-y-2">
                  <span class="title-block font-wide font-bold text-white">{{ stage.title }}</span>

                  <span
                    v-if="stage.duration"
                    class="bg-ink rounded-pill text-small shrink-0 px-[1.1em] py-[0.5em] text-white/80"
                  >
                    {{ stage.duration }}
                  </span>
                </span>

                <span
                  v-if="stage.description"
                  class="mt-[0.9rem] block max-w-[70ch] leading-relaxed text-white/55"
                >
                  {{ stage.description }}
                </span>
              </span>

              <span
                class="bg-ink grid size-[2.75rem] shrink-0 place-items-center rounded-full transition-colors lg:size-[3.25rem]"
                :class="openIndex === index ? 'text-brand' : 'text-white/40'"
                aria-hidden="true"
              >
                <svg class="size-[40%]" viewBox="0 0 20 20" fill="none">
                  <path
                    d="M4 10h12"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                  />
                  <path
                    v-if="openIndex !== index"
                    d="M10 4v12"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                  />
                </svg>
              </span>
            </button>
          </h3>

          <!-- Ochiluvchi qism -->
          <div
            :id="`${uid}-panel-${index}`"
            role="region"
            :aria-labelledby="`${uid}-button-${index}`"
            class="panel"
            :class="{ 'is-open': openIndex === index }"
            :inert="openIndex !== index"
          >
            <div class="overflow-hidden">
              <div class="px-[1.75rem] pb-[1.75rem] md:px-[2.5rem] md:pb-[2.5rem]">
                <div class="grid gap-[var(--spacing-block)] lg:grid-cols-[1.35fr_1fr]">
                  <div v-if="stage.topics?.length">
                    <p class="font-wide font-bold text-white">{{ topicsLabelText }}</p>

                    <ul class="mt-[1.25rem] flex flex-col gap-[0.85rem]">
                      <li
                        v-for="topic in stage.topics"
                        :key="topic"
                        class="flex items-start gap-[0.75rem] text-white/70"
                      >
                        <svg
                          class="text-brand mt-[0.15em] size-[1.15em] shrink-0"
                          viewBox="0 0 20 20"
                          fill="none"
                          aria-hidden="true"
                        >
                          <circle
                            cx="10"
                            cy="10"
                            r="8.25"
                            stroke="currentColor"
                            stroke-width="1.4"
                          />
                          <path
                            d="m6.6 10.2 2.3 2.3 4.5-4.7"
                            stroke="currentColor"
                            stroke-width="1.6"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          />
                        </svg>
                        <span class="leading-snug">{{ topic }}</span>
                      </li>
                    </ul>
                  </div>

                  <div v-if="badgesOf(stage).length">
                    <p class="font-wide font-bold text-white">{{ toolsLabelText }}</p>

                    <ul class="mt-[1.25rem] flex flex-wrap gap-[0.6rem]">
                      <li
                        v-for="badge in badgesOf(stage)"
                        :key="badge.label"
                        class="bg-ink rounded-pill flex items-center gap-[0.6em] px-[1.05em] py-[0.6em]"
                      >
                        <img
                          loading="lazy"
                          decoding="async"
                          :src="badge.icon"
                          alt=""
                          aria-hidden="true"
                          class="size-[1.5em] shrink-0"
                        />
                        <span class="text-[var(--text-body)] text-white">{{ badge.label }}</span>
                      </li>
                    </ul>
                  </div>
                </div>

                <!-- Bosqich natijasi -->
                <div
                  v-if="stage.result"
                  class="result rounded-block mt-[var(--spacing-block)] flex flex-col items-start gap-[1.5rem] p-[1.75rem] sm:flex-row sm:items-center sm:gap-[6%] md:p-[2.25rem]"
                >
                  <p class="title-block font-wide shrink-0 font-bold text-white sm:max-w-[7ch]">
                    {{ t('courses.stageResult') }}
                  </p>

                  <p class="flex-1 leading-relaxed text-white">{{ stage.result }}</p>

                  <img
                    :src="checkBadge"
                    alt=""
                    aria-hidden="true"
                    loading="lazy"
                    class="size-[3.5rem] shrink-0 object-contain md:size-[4.5rem]"
                  />
                </div>
              </div>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
/* Balandlikni o'lchamasdan silliq ochish/yopish */
.panel {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.35s ease;
}

.panel.is-open {
  grid-template-rows: 1fr;
}

.result {
  background: linear-gradient(90deg, #e9491f 0%, #b8401f 18%, #6b3475 62%, #3b3a8c 100%);
}

@media (prefers-reduced-motion: reduce) {
  .panel {
    transition: none;
  }
}
</style>
