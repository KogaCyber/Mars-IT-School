<script setup>
/**
 * «О курсе» bo'limi — Figma: chapda yorliq va yirik sarlavha, o'ng yarmda
 * izoh; ostida dastur/asboblar yorliqlari va cheksiz aylanuvchi mavzu
 * kartochkalari.
 *
 * Kartochkalar lentasi kontent maydonidan kengroq: chapda konteyner chetidan
 * boshlanadi, o'ngda esa ekran chetiga qarab davom etadi (maketdagi kabi).
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import glow from '@/assets/images/about-glow.webp'
import InfiniteCarousel from '@/components/base/InfiniteCarousel.vue'
import OutlineIcon from '@/components/base/OutlineIcon.vue'
import { TECH } from '@/data/directions'

const { t } = useI18n()

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
  /** `TECH` kalitlari — masalan `['html', 'css']`. */
  tools: { type: Array, default: () => [] },
  /** `[{ title, description, icon }]` — aylanuvchi kartochkalar. */
  topics: { type: Array, required: true },
  /** Bo'sh qoldirilsa — «Kurs haqida» tarjimasi ishlatiladi. */
  eyebrow: { type: String, default: '' },
})

const eyebrowText = computed(() => props.eyebrow || t('courses.aboutEyebrow'))

/** Noma'lum kalitlar tushib qolsin — maket buzilmaydi. */
const badges = computed(() => props.tools.map((key) => TECH[key]).filter(Boolean))
</script>

<template>
  <section class="section bg-ink relative overflow-hidden">
    <!-- Fon nuri: sarlavha ostidan kartochkalar orqasiga tushadi -->
    <img
      loading="lazy"
      decoding="async"
      :src="glow"
      alt=""
      aria-hidden="true"
      class="animate-glow pointer-events-none absolute top-[52%] left-[46%] w-[190%] max-w-none -translate-x-1/2 -translate-y-1/2 opacity-70 select-none lg:w-[100%]"
    />

    <div class="relative">
      <div class="container-page sm:block lg:flex justify-between items-center">
        <div>
          <p v-reveal class="eyebrow">{{ eyebrowText }}</p>

          <h2
            v-reveal
            class="title-hero font-wide mt-[2.5%] max-w-[15ch] font-bold text-white mb-[15%]"
          >
            {{ title }}
          </h2>

          <template v-if="badges.length">
            <p v-reveal class="font-wide text-lead mt-[7%] font-bold text-white">
              {{ t('courses.toolsTitle') }}
            </p>

            <ul v-reveal class="mt-[1.8%] flex flex-wrap gap-[0.65rem]">
              <li
                v-for="badge in badges"
                :key="badge.label"
                class="bg-surface rounded-pill flex items-center gap-[0.65em] px-[1.15em] py-[0.7em]"
              >
                <img
                  loading="lazy"
                  decoding="async"
                  :src="badge.icon"
                  alt=""
                  aria-hidden="true"
                  class="size-[1.7em] shrink-0"
                />
                <span class="text-lead text-white">{{ badge.label }}</span>
              </li>
            </ul>
          </template>
        </div>

        <div class="mt-[6%]">
          <p
            v-reveal="{ delay: 120 }"
            class="text-lead max-w-[52ch] leading-relaxed text-white/70 lg:col-start-2"
          >
            {{ description }}
          </p>
        </div>
      </div>

      <!-- Mavzu kartochkalari: cheksiz aylanadi -->
      <div class="mt-[5.5%]">
        <InfiniteCarousel
          :speed="38"
          style="mask-image: linear-gradient(to right, #000 0, #000 90%, transparent 100%)"
        >
          <article
            v-for="topic in topics"
            :key="topic.title"
            class="rounded-block relative flex size-[15rem] shrink-0 flex-col border border-white/[0.07] bg-white/[0.045] p-[1.6rem] backdrop-blur-md transition duration-300 hover:-translate-y-1 hover:border-white/15 hover:bg-white/[0.075] lg:size-[17rem] lg:p-[1.9rem]"
          >
            <h3
              class="font-wide text-[1.0625rem] leading-snug font-bold whitespace-pre-line text-white"
            >
              {{ topic.title }}
            </h3>

            <p class="mt-[1.1rem] text-[var(--text-body)] leading-relaxed text-white/55">
              {{ topic.description }}
            </p>

            <OutlineIcon
              :name="topic.icon"
              class="mt-auto size-[2.5rem] shrink-0 text-white/10 lg:size-[2.75rem]"
            />
          </article>
        </InfiniteCarousel>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Lenta chapda konteyner cheti bilan tekislanadi, o'ngda cheklanmaydi. */
.topics {
  padding-left: max((100% - 1180px) / 2, 4%);
}

@media (min-width: 1024px) {
  .topics {
    padding-left: max((100% - 1180px) / 2, 9%);
  }
}
</style>
