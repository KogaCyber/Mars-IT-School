<script setup>
/**
 * SPACE platformasining jonli maketi (rasm emas — to'liq kod bilan chizilgan).
 *
 * Chapdagi menyu bosilganda o'ng tomondagi kontent almashadi.
 * Kichik ekranlarda menyu gorizontal yorliqlarga aylanadi.
 */
import { useResizeObserver } from '@vueuse/core'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { SPACE_MENU, SPACE_VIEWS } from '@/data/spacePlatform'
import { useLocalized } from '@/i18n/localize'

const { t } = useI18n()

/** Faol bo'lim tashqarida ham boshqariladi (mobil yorliqlar bilan umumiy holat). */
const activeId = defineModel({ type: String, default: SPACE_MENU[0].id })
const views = useLocalized(SPACE_VIEWS)
const view = computed(() => views.value[activeId.value])

/**
 * Qator ostidagi izoh: sana alohida tarjima qilinadi, shuning uchun
 * `meta` shabloniga (`Muddat: {d}`) qo'yiladi.
 */
function rowMeta(row) {
  if (!row.meta) return ''
  return row.metaDate ? row.meta.replace('{d}', row.metaDate) : row.meta
}

/* --- Tor ekranda maketni butunlay ko'rsatish uchun proporsional kichraytirish --- */
// Maket shu kenglikda chizilgan; kichik ekranda shu o'lcham saqlanib, scale bilan siqiladi.
const BASE_WIDTH = 960
const COMPACT_BELOW = 1024

const wrapper = ref(null)
const board = ref(null)
const scale = ref(1)
const wrapperHeight = ref(null)

function measure() {
  const wrap = wrapper.value
  const inner = board.value
  if (!wrap || !inner) return

  const available = wrap.offsetWidth
  if (available >= COMPACT_BELOW) {
    scale.value = 1
    wrapperHeight.value = null
    return
  }

  scale.value = available / BASE_WIDTH
  wrapperHeight.value = inner.offsetHeight * scale.value
}

useResizeObserver(wrapper, measure)
useResizeObserver(board, measure)

const isCompact = computed(() => scale.value < 1)

const STAT_TONES = {
  brand: 'text-brand bg-brand/12',
  violet: 'text-[#a78bfa] bg-[#a78bfa]/12',
  amber: 'text-[#fbbf24] bg-[#fbbf24]/12',
  green: 'text-[#4ade80] bg-[#4ade80]/12',
}

const STATUS_TONES = {
  brand: 'text-brand bg-brand/12',
  violet: 'text-[#a78bfa] bg-[#a78bfa]/12',
  green: 'text-[#4ade80] bg-[#4ade80]/12',
  muted: 'text-muted bg-white/5',
}

/** Menyu ikonkalari — sodda chiziqli belgilar. */
const ICONS = {
  book: 'M4 5.5A1.5 1.5 0 0 1 5.5 4H10v12H5.5A1.5 1.5 0 0 1 4 14.5v-9ZM10 4h4.5A1.5 1.5 0 0 1 16 5.5v9a1.5 1.5 0 0 1-1.5 1.5H10',
  play: 'M4 6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Zm4 2.5v3l3-1.5-3-1.5Z',
  star: 'm10 3.5 2 4.2 4.5.6-3.3 3.2.8 4.5-4-2.2-4 2.2.8-4.5L3.5 8.3l4.5-.6 2-4.2Z',
  trophy: 'M6 4h8v3a4 4 0 0 1-8 0V4Zm0 1H4v1a2 2 0 0 0 2 2m8-3h2v1a2 2 0 0 1-2 2m-4 4v3m-2.5 0h5',
  chat: 'M4 5.5A1.5 1.5 0 0 1 5.5 4h9A1.5 1.5 0 0 1 16 5.5v6A1.5 1.5 0 0 1 14.5 13H8l-4 3v-3.5A1.5 1.5 0 0 1 4 11.5v-6Z',
  bag: 'M5 6h10l-.8 9.2a1.5 1.5 0 0 1-1.5 1.3H7.3a1.5 1.5 0 0 1-1.5-1.3L5 6Zm2.5 0V5a2.5 2.5 0 0 1 5 0v1',
}

// Kalendar uchun namunaviy hafta
const CALENDAR_DAYS = [19, 20, 21, 22, 23, 24, 25]
const calendarLabels = computed(() => t('platform.weekdays').split(','))

// Yaqin muddatlar — «Uy vazifalari» bo'limidagi dastlabki uchta topshiriq.
const deadlines = computed(() =>
  views.value.homework.rows
    .filter((row) => row.metaDate && row.status.tone === 'brand')
    .slice(0, 3)
    .map((row) => ({ title: row.title, subtitle: row.subtitle, date: row.metaDate })),
)
</script>

<template>
  <!-- Tor ekranda maket to'liq ko'rinishi uchun proporsional kichraytiriladi -->
  <div
    ref="wrapper"
    class="overflow-hidden"
    :style="wrapperHeight ? { height: `${wrapperHeight}px` } : null"
  >
    <div
      ref="board"
      class="bg-ink rounded-block border-line overflow-hidden border"
      :style="
        isCompact
          ? { width: `${BASE_WIDTH}px`, transform: `scale(${scale})`, transformOrigin: 'top left' }
          : null
      "
    >
      <div class="grid grid-cols-[15rem_1fr]">
        <!-- Chap menyu -->
        <nav class="border-line flex flex-col gap-2 border-e p-4" :aria-label="t('platform.menuLabel')">
          <span class="mb-2 block px-3 font-wide text-[1.1rem] font-bold text-white">
            MARS<span class="text-brand">°</span>
          </span>

          <button
            v-for="item in SPACE_MENU"
            :key="item.id"
            type="button"
            class="flex shrink-0 items-center gap-2.5 rounded-xl px-3 py-2.5 text-left text-[0.82rem] whitespace-nowrap transition"
            :class="
              activeId === item.id
                ? 'border-brand/60 text-brand bg-brand/10 border'
                : 'border border-transparent text-white/70 hover:bg-white/5 hover:text-white'
            "
            :aria-current="activeId === item.id ? 'true' : undefined"
            @click="activeId = item.id"
          >
            <svg class="size-[1.15rem] shrink-0" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                :d="ICONS[item.icon]"
                stroke="currentColor"
                stroke-width="1.3"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            {{ t(`spaceMenu.${item.id}`) }}
          </button>

          <!-- O'quvchi kartochkasi -->
          <div class="border-line mt-auto rounded-2xl border bg-white/[0.03] p-3">
            <div class="flex items-center gap-2.5">
              <span
                class="grid size-9 shrink-0 place-items-center rounded-full font-wide text-[0.7rem] font-bold text-white"
                style="background: linear-gradient(135deg, #e94921, #3b2f7a)"
                aria-hidden="true"
              >
                {{ t('platform.studentInitials') }}
              </span>
              <span>
                <span class="block text-[0.8rem] text-white">{{ t('platform.studentName') }}</span>
                <span class="text-muted block text-[0.7rem]">{{ t('platform.studentRole') }}</span>
              </span>
            </div>

            <p class="mt-3 flex justify-between text-[0.7rem] text-white/70">
              <span>{{ t('platform.level', { level: 12 }) }}</span>
              <span class="text-muted">{{ t('platform.xp', { current: '2 450', total: '3 000' }) }}</span>
            </p>
            <span class="mt-1.5 block h-1.5 overflow-hidden rounded-full bg-white/10">
              <span class="bg-brand block h-full rounded-full" style="width: 82%" />
            </span>
          </div>
        </nav>

        <!-- Kontent -->
        <div class="p-6">
          <Transition name="view" mode="out-in">
            <div :key="activeId">
              <!-- Sarlavha -->
              <header class="flex items-start justify-between gap-4">
                <div>
                  <h3 class="font-wide text-[1.4rem] font-bold text-white">
                    {{ view.title }}
                  </h3>
                  <p class="text-muted mt-1 text-[0.8rem]">{{ view.subtitle }}</p>
                </div>

                <div class="flex shrink-0 items-center gap-3">
                  <span class="relative grid size-8 place-items-center rounded-full bg-white/5">
                    <svg
                      class="size-4 text-white/70"
                      viewBox="0 0 20 20"
                      fill="none"
                      aria-hidden="true"
                    >
                      <path
                        d="M6 8a4 4 0 1 1 8 0c0 3 1.5 4 1.5 4h-11S6 11 6 8Zm2.5 6.5a1.5 1.5 0 0 0 3 0"
                        stroke="currentColor"
                        stroke-width="1.3"
                        stroke-linecap="round"
                      />
                    </svg>
                    <span class="bg-brand absolute -top-0.5 -right-0.5 size-2 rounded-full" />
                  </span>

                  <span
                    class="grid size-8 place-items-center rounded-full font-wide text-[0.65rem] font-bold text-white"
                    style="background: linear-gradient(135deg, #e94921, #3b2f7a)"
                    aria-hidden="true"
                  >
                    {{ t('platform.studentInitials') }}
                  </span>
                </div>
              </header>

              <!-- Statistika -->
              <ul class="mt-4 grid grid-cols-4 gap-2.5">
                <li
                  v-for="stat in view.stats"
                  :key="stat.label"
                  class="border-line flex items-center gap-2.5 rounded-2xl border bg-white/[0.02] p-3"
                >
                  <span
                    class="grid size-8 shrink-0 place-items-center rounded-xl text-[0.7rem] font-bold"
                    :class="STAT_TONES[stat.tone]"
                    aria-hidden="true"
                  >
                    ●
                  </span>
                  <span>
                    <span class="block font-wide text-[1.05rem] font-bold text-white">
                      {{ stat.value }}
                    </span>
                    <span class="text-muted block text-[0.7rem]">{{ stat.label }}</span>
                  </span>
                </li>
              </ul>

              <div class="mt-4 grid grid-cols-[1fr_16rem] gap-4">
                <!-- Ro'yxat -->
                <div class="border-line rounded-2xl border bg-white/[0.02] p-3">
                  <ul class="border-line flex gap-4 overflow-x-auto border-b pb-2 text-[0.78rem]">
                    <li v-for="(tab, index) in view.tabs" :key="tab">
                      <span
                        class="block pb-1 whitespace-nowrap"
                        :class="index === 0 ? 'border-brand text-brand border-b-2' : 'text-muted'"
                      >
                        {{ tab }}
                      </span>
                    </li>
                  </ul>

                  <ul class="divide-line mt-1 divide-y">
                    <li
                      v-for="row in view.rows"
                      :key="row.title"
                      class="flex items-center gap-3 py-2.5"
                    >
                      <span
                        class="grid size-8 shrink-0 place-items-center rounded-xl text-[0.7rem] font-bold"
                        :style="{ backgroundColor: row.tech.color, color: row.tech.text }"
                        aria-hidden="true"
                      >
                        {{ row.tech.label }}
                      </span>

                      <span class="min-w-0 flex-1">
                        <span class="block truncate text-[0.82rem] text-white">{{
                          row.title
                        }}</span>
                        <span class="text-muted block truncate text-[0.72rem]">
                          {{ row.subtitle }}
                        </span>
                      </span>

                      <span class="shrink-0 text-right">
                        <span
                          class="rounded-pill w-fit shrink-0 px-2.5 py-1 text-[0.68rem] whitespace-nowrap"
                          :class="STATUS_TONES[row.status.tone]"
                        >
                          {{ row.status.label }}
                        </span>
                        <span class="text-muted mt-1 block text-[0.68rem]">{{ rowMeta(row) }}</span>
                      </span>

                      <span
                        v-if="row.value"
                        class="w-12 shrink-0 text-right font-wide text-[0.8rem] font-bold text-white"
                      >
                        {{ row.value }}
                      </span>
                    </li>
                  </ul>
                </div>

                <!-- O'ng ustun -->
                <aside class="flex flex-col gap-4">
                  <div class="border-line rounded-2xl border bg-white/[0.02] p-3">
                    <p class="text-[0.8rem] text-white">{{ view.aside.title }}</p>

                    <template v-if="view.aside.type === 'calendar'">
                      <ul class="text-muted mt-3 grid grid-cols-7 gap-1 text-center text-[0.62rem]">
                        <li v-for="label in calendarLabels" :key="label">{{ label }}</li>
                      </ul>
                      <ul class="mt-1 grid grid-cols-7 gap-1 text-center text-[0.7rem]">
                        <li
                          v-for="day in CALENDAR_DAYS"
                          :key="day"
                          class="grid h-7 place-items-center rounded-lg"
                          :class="day === 21 ? 'bg-brand text-white' : 'text-white/70'"
                        >
                          {{ day }}
                        </li>
                      </ul>
                    </template>

                    <!-- Oddiy diagramma (SVG) -->
                    <svg
                      v-else
                      class="mt-3 w-full"
                      viewBox="0 0 120 44"
                      fill="none"
                      role="img"
                      :aria-label="t('platform.progressChart')"
                    >
                      <polyline
                        points="2,38 20,30 38,32 56,22 74,24 92,12 118,6"
                        stroke="#e94921"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <circle cx="118" cy="6" r="3" fill="#e94921" />
                    </svg>
                  </div>

                  <div class="border-line rounded-2xl border bg-white/[0.02] p-3">
                    <p class="text-[0.8rem] text-white">{{ t('platform.upcomingDeadlines') }}</p>
                    <ul class="mt-2.5 flex flex-col gap-2.5">
                      <li
                        v-for="deadline in deadlines"
                        :key="deadline.title"
                        class="flex items-start justify-between gap-2"
                      >
                        <span class="min-w-0">
                          <span class="block truncate text-[0.75rem] text-white">
                            {{ deadline.title }}
                          </span>
                          <span class="text-muted block truncate text-[0.68rem]">
                            {{ deadline.subtitle }}
                          </span>
                        </span>
                        <span class="text-brand shrink-0 text-[0.68rem]">{{ deadline.date }}</span>
                      </li>
                    </ul>
                  </div>
                </aside>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-enter-active,
.view-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}

.view-enter-from {
  opacity: 0;
  transform: translateY(0.5rem);
}

.view-leave-to {
  opacity: 0;
  transform: translateY(-0.35rem);
}
</style>
