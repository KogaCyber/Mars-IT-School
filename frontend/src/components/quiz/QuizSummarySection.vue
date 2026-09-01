<script setup>
/**
 * «Итог результата теста» — natijaning qisqa xulosasi.
 *
 * Qatorlar haqiqiy ma'lumotdan yig'iladi: yo'nalish va uning moslik foizi,
 * eng kuchli ikkita ko'nikma (foizi bilan), keyingi qadam va yo'nalishga oid
 * izoh. Ma'lumot yetishmasa (masalan ko'nikmalar bo'sh) — qator tushib qoladi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  /** G'olib natija: `{ code, title }`. */
  outcome: { type: Object, default: null },
  /** `[{ code, title, percent }]` — moslik foizlari. */
  matches: { type: Array, default: () => [] },
  /** `[{ code, title, percent }]` — ko'nikmalar, kamayish tartibida. */
  skills: { type: Array, default: () => [] },
  /** Yo'nalishga oid izoh (pastki qator). */
  note: { type: String, default: '' },
  /** Eng past ko'nikma — «zona o'sishi» qatori uchun (bo'lmasa — qator yo'q). */
  growthSkill: { type: Object, default: null },
})

const rows = computed(() => {
  const items = []

  const match = props.matches.find((item) => item.code === props.outcome?.code)
  if (props.outcome) {
    const percent = match ? t('quiz.summaryMatch', { percent: match.percent }) : ''
    items.push(t('quiz.summaryDirection', { name: props.outcome.title, percent }))
  }

  const [first, second] = props.skills
  if (first) items.push(t('quiz.summaryFirst', { title: first.title, percent: first.percent }))
  if (second) items.push(t('quiz.summarySecond', { title: second.title, percent: second.percent }))

  if (props.growthSkill) {
    items.push(
      t('quiz.summaryGrowth', {
        title: props.growthSkill.title,
        percent: props.growthSkill.percent,
      }),
    )
  }

  items.push(t('quiz.summaryNextStep'))

  return items
})
</script>

<template>
  <section v-reveal class="bg-ink pb-[var(--spacing-section)]">
    <div class="container-page">
      <div class="bg-surface rounded-[2.5rem] p-7 sm:p-10 lg:p-14">
        <!-- Sarlavha qatori -->
        <header class="flex items-start gap-5">
          <span
            class="grid size-12 shrink-0 place-items-center rounded-full border border-white/20 text-white"
            aria-hidden="true"
          >
            <svg class="size-6" viewBox="0 0 24 24" fill="none">
              <path
                d="m7.5 12.4 3 3 6-6.8"
                stroke="currentColor"
                stroke-width="1.6"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </span>

          <div>
            <h2 class="text-brand font-wide text-[1.05rem] font-bold">{{ t('quiz.summaryTitle') }}</h2>
            <p class="font-wide mt-1.5 text-[1.05rem] leading-snug font-bold text-white">
              {{ t('quiz.summarySubtitle') }}
            </p>
          </div>
        </header>

        <!-- Xulosa qatorlari -->
        <div class="bg-ink mt-10 rounded-[1.75rem] p-7 lg:p-10">
          <ul class="flex flex-col gap-5">
            <li v-for="row in rows" :key="row" class="flex items-start gap-3.5">
              <span class="text-white/50" aria-hidden="true">
                <svg class="mt-0.5 size-5" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="8.2" stroke="currentColor" stroke-width="1.3" />
                  <path
                    d="m8.6 12.2 2.4 2.4 4.4-5"
                    stroke="currentColor"
                    stroke-width="1.4"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>

              <p class="font-wide font-bold text-white">{{ row }}</p>
            </li>

            <!-- Izoh: ohangi past, shu sababli kulrang -->
            <li v-if="note" class="flex items-start gap-3.5">
              <span class="text-white/30" aria-hidden="true">
                <svg class="mt-0.5 size-5" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="8.2" stroke="currentColor" stroke-width="1.3" />
                  <path
                    d="M12 11v5M12 8.2h.01"
                    stroke="currentColor"
                    stroke-width="1.4"
                    stroke-linecap="round"
                  />
                </svg>
              </span>

              <p class="font-wide font-bold text-white/35">{{ note }}</p>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>
