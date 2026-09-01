<script setup>
/**
 * «Совпадение с Frontend / Backend» — natija sahifasidagi moslik kartochkalari.
 *
 * Foizlar backenddan keladi (`/quiz-results/<id>/` → `matches`): ballar 100% ga
 * keltirilgan. Har bir kartochkada foiz paneli, shu foizga mos progress chizig'i
 * va yo'nalishning texnologiya yorliqlari bor.
 *
 * Maketda ikkala kartochkada bir xil texnologiyalar va bir xil uzunlikdagi
 * chiziq turgan edi — bu ma'lumotga zid, shuning uchun:
 *   • chiziq uzunligi haqiqiy foizni ko'rsatadi,
 *   • yorliqlar har bir yo'nalishning o'z stek'i,
 *   • g'olib kartochka brend rangli chegara va «Ваше направление» belgisi oladi.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import cssIcon from '@/assets/icons/tech-css.svg'
import htmlIcon from '@/assets/icons/tech-html.svg'
import jsIcon from '@/assets/icons/tech-js.svg'
import pythonIcon from '@/assets/icons/tech-python.svg'
import reactIcon from '@/assets/icons/tech-react.svg'
import { DIRECTION_STACKS } from '@/data/quizOutcomes'

const { t } = useI18n()

const props = defineProps({
  /** `[{ code, title, percent }]` — backenddan kelgan moslik foizlari. */
  matches: { type: Array, default: () => [] },
  /** G'olib yo'nalish kodi. */
  activeCode: { type: String, default: '' },
})

const ICONS = { html: htmlIcon, css: cssIcon, js: jsIcon, react: reactIcon, python: pythonIcon }

/** Maketdagi tartib: avval Frontend, keyin Backend. */
const ORDER = ['frontend', 'backend']

const cards = computed(() =>
  [...props.matches]
    .sort((a, b) => ORDER.indexOf(a.code) - ORDER.indexOf(b.code))
    .map((item) => ({
      ...item,
      stack: DIRECTION_STACKS[item.code] || [],
      isActive: item.code === props.activeCode,
    })),
)
</script>

<template>
  <section v-if="cards.length" v-reveal class="bg-ink pb-[var(--spacing-block)]">
    <div class="container-page grid gap-6 lg:grid-cols-2">
      <article
        v-for="card in cards"
        :key="card.code"
        class="bg-surface flex flex-col rounded-[2rem] border p-7 transition-colors lg:p-9"
        :class="card.isActive ? 'border-brand/45' : 'border-transparent'"
      >
        <!-- Foiz paneli -->
        <div
          class="relative overflow-hidden rounded-pill px-8 py-6"
          :class="card.isActive ? 'panel-brand' : 'panel-violet'"
        >
          <p
            class="font-wide relative text-[clamp(1.75rem,3vw,2.5rem)] leading-none font-bold text-white"
          >
            {{ card.percent }}%
          </p>
          <p class="font-wide relative mt-2.5 font-bold text-white/80">
            {{ t('quiz.matchWith', { title: card.title }) }}
          </p>
        </div>

        <!-- Progress: uzunligi foizga teng -->
        <div class="mt-7 h-1.5 overflow-hidden rounded-pill bg-white/10">
          <div
            class="h-full rounded-pill transition-all duration-700"
            :style="{
              width: `${card.percent}%`,
              background: 'linear-gradient(90deg, #e2451f 0%, #a63a5a 55%, #3b2f7a 100%)',
            }"
          />
        </div>

        <!-- Texnologiya yorliqlari -->
        <ul class="mt-7 flex flex-wrap gap-3">
          <li
            v-for="tech in card.stack"
            :key="tech.label"
            class="bg-ink flex items-center gap-2.5 rounded-pill py-2.5 pr-5 pl-3"
          >
            <img
              loading="lazy"
              decoding="async"
              v-if="ICONS[tech.icon]"
              :src="ICONS[tech.icon]"
              alt=""
              aria-hidden="true"
              class="size-6 object-contain"
            />
            <span v-else class="bg-brand size-2 rounded-full" aria-hidden="true" />
            <span class="text-white">{{ tech.label }}</span>
          </li>
        </ul>

        <p v-if="card.isActive" class="text-brand mt-6 font-medium">{{ t('quiz.yourDirection') }}</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
/* Foiz paneli ortidagi nur: g'olibda issiq, ikkinchisida sovuq */
.panel-brand {
  background:
    radial-gradient(120% 140% at 12% 20%, rgba(226, 69, 31, 0.5), transparent 62%), #101012;
}

.panel-violet {
  background:
    radial-gradient(120% 140% at 12% 20%, rgba(84, 92, 214, 0.45), transparent 62%), #101012;
}
</style>
