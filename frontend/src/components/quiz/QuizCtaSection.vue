<script setup>
/**
 * «Приведите ребёнка в MARS IT уже сегодня» — natija sahifasidagi chaqiruv bloki.
 *
 * Maket: yorliq va yirik sarlavha; ostida 2×2 kapsula kartochkalar (o'ng chetida
 * issiq nur), so'ng uchta raqam kapsulasi va ikkita tugma.
 *
 * Raqamlar admin paneldan keladi (`/statistics/`) — maketdagi qiymatlar faqat
 * ma'lumot bo'lmaganda zaxira sifatida ishlatiladi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseButton from '@/components/base/BaseButton.vue'
import { useSiteStore } from '@/stores/site'

const props = defineProps({
  /** `/statistics/` javobidagi ro'yxat: `[{ id, value, label }]`. */
  stats: { type: Array, default: () => [] },
})

const { t } = useI18n()
const site = useSiteStore()

/** Maketdagi to'rtta sabab — maktab haqida, natijaga bog'liq emas. */
const reasons = computed(() =>
  [1, 2, 3, 4].map((n) => ({
    title: t(`quiz.ctaCard${n}Title`),
    text: t(`quiz.ctaCard${n}Text`),
  })),
)

/** Ma'lumot bo'lmaganda ko'rsatiladigan raqamlar. */
const fallbackStats = computed(() => [
  { id: 'students', value: '5000+', label: t('quiz.ctaStatStudents') },
  { id: 'branches', value: '7', label: t('quiz.ctaStatBranches') },
  { id: 'years', value: '5', label: t('quiz.ctaStatYears') },
])

const numbers = computed(() =>
  props.stats.length ? props.stats.slice(0, 3) : fallbackStats.value,
)

/** Telegram havolasi sozlamalarda bo'lmasa — ariza sahifasiga yo'naltiramiz. */
const telegramUrl = computed(() => site.settings.telegram_url || '')
</script>

<template>
  <section v-reveal class="bg-ink pb-[var(--spacing-block)]">
    <div class="container-page">
      <div class="bg-surface rounded-[2.5rem] p-7 sm:p-10 lg:p-14">
        <p class="eyebrow">{{ t('quiz.ctaEyebrow') }}</p>

        <h2 class="font-wide title-cta mt-7 font-bold text-white">
          <span v-for="line in t('quiz.ctaTitle').split('\n')" :key="line" class="block">
            {{ line }}
          </span>
        </h2>

        <!-- Sabablar -->
        <ul class="mt-10 grid gap-5 lg:grid-cols-2">
          <li
            v-for="reason in reasons"
            :key="reason.title"
            class="bg-ink relative h-full overflow-hidden rounded-[2rem] p-8 lg:rounded-[4rem] lg:px-12 lg:py-9"
          >
            <span
              class="reason-glow pointer-events-none absolute inset-y-0 right-0 w-[40%]"
              aria-hidden="true"
            />

            <h3 class="font-wide relative font-bold text-white">{{ reason.title }}</h3>
            <p class="relative mt-3 max-w-[52ch] leading-relaxed text-white/60">
              {{ reason.text }}
            </p>
          </li>
        </ul>

        <!-- Raqamlar -->
        <ul class="mt-5 grid gap-5 md:grid-cols-3">
          <li
            v-for="item in numbers"
            :key="item.id || item.label"
            class="bg-ink relative overflow-hidden rounded-pill px-8 py-7 text-center"
          >
            <span
              class="number-glow pointer-events-none absolute inset-y-0 left-0 w-[40%]"
              aria-hidden="true"
            />

            <p
              class="font-wide relative text-[clamp(1.5rem,2.4vw,2rem)] leading-none font-bold text-white"
            >
              {{ item.value }}
            </p>
            <p class="font-wide relative mt-2.5 font-bold text-white/70">{{ item.label }}</p>
          </li>
        </ul>

        <!-- Tugmalar -->
        <div class="mt-5 grid gap-5 md:grid-cols-2">
          <BaseButton
            v-if="telegramUrl"
            size="lg"
            :href="telegramUrl"
            class="font-wide h-[4rem] font-bold"
            block
          >
            {{ t('quiz.ctaTelegram') }}
          </BaseButton>

          <BaseButton
            v-else
            size="lg"
            class="font-wide h-[4rem] font-bold"
            block
            :to="{ name: 'application', query: { source: 'quiz' } }"
          >
            {{ t('quiz.ctaTrial') }}
          </BaseButton>

          <BaseButton
            size="lg"
            variant="ghost"
            class="bg-ink hover:bg-ink/70 font-wide h-[4rem] font-bold"
            block
            :to="{ name: 'quiz' }"
          >
            {{ t('quiz.ctaRetake') }}
          </BaseButton>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Maketda sarlavha bo'lim sarlavhalaridan yirikroq */
.title-cta {
  font-size: clamp(1.6rem, 3.1vw, 3rem);
  line-height: 1.1;
}

/* Kartochka chetidagi issiq nur */
.reason-glow {
  background: radial-gradient(closest-side at 75% 50%, rgba(226, 69, 31, 0.26), transparent 78%);
}

/* Raqam kapsulasidagi sovuq nur */
.number-glow {
  background: radial-gradient(closest-side at 25% 50%, rgba(84, 92, 214, 0.32), transparent 78%);
}
</style>
