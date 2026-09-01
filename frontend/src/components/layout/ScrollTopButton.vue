<script setup>
/**
 * Ekranning o'ng pastida turadigan «tepaga» tugmasi.
 * Sahifa boshida ko'rinmaydi, skroll qilinganda paydo bo'ladi.
 */
import { useWindowScroll } from '@vueuse/core'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { y } = useWindowScroll()

// Bir ekran balandligidan ko'proq siljiganda ko'rinadi.
const isVisible = computed(() => y.value > 400)

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <Transition name="fab">
    <button
      v-show="isVisible"
      type="button"
      class="bg-brand hover:bg-brand-hover press fixed right-[4%] bottom-[4%] z-40 grid size-[2.75rem] place-items-center rounded-pill text-white shadow-lg transition lg:size-[3rem]"
      :aria-label="t('common.scrollTop')"
      @click="scrollToTop"
    >
      <svg class="size-[45%]" viewBox="0 0 14 14" fill="none" aria-hidden="true">
        <path
          d="M7 11.5V2.5M7 2.5L3 6.5M7 2.5l4 4"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </button>
  </Transition>
</template>

<style scoped>
.fab-enter-active,
.fab-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}
.fab-enter-from,
.fab-leave-to {
  opacity: 0;
  transform: translateY(0.75rem);
}
</style>
