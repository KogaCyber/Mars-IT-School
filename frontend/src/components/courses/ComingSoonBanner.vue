<script setup>
/**
 * «Скоро...» banneri — Figma: chapdan o'ngga ko'kdan to'q sariqqa o'tuvchi
 * gradient, chapda yirik sarlavha, o'rtada matn, o'ngda qo'l silkiyotgan
 * astronavt (blok chekkasidan biroz chiqib turadi).
 */
import astronaut from '@/assets/images/skoro.webp'
import { COMING_SOON } from '@/data/directions'
import { useLocalized } from '@/i18n/localize'

const comingSoon = useLocalized(COMING_SOON)
</script>

<template>
  <div class="banner rounded-block relative overflow-hidden px-[6%] py-[5%]">
    <div class="relative grid items-center gap-[6%] md:grid-cols-[auto_1fr_auto] md:gap-[4%]">
      <h3 class="title-hero font-wide font-bold text-white">{{ comingSoon.title }}</h3>

      <p class="text-lead max-w-[34ch] leading-relaxed text-white">
        {{ comingSoon.description }}
      </p>

      <img
        :src="astronaut"
        alt=""
        aria-hidden="true"
        loading="lazy"
        class="animate-float mx-auto w-[45%] max-w-[15rem] object-contain md:mx-0 md:-my-[12%] md:w-[16vw] md:max-w-[19rem]"
      />
    </div>
  </div>
</template>

<style scoped>
/* Ko'k (navy) → to'q sariq gradient; o'ng chetda nur kuchayadi */
.banner {
  background:
    radial-gradient(120% 140% at 88% 55%, rgb(233 73 33 / 0.55) 0%, transparent 60%),
    linear-gradient(100deg, #2b2f63 0%, #2a2a3f 42%, #2c2320 72%, #3a2019 100%);
}
</style>
