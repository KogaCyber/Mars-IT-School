<script setup>
/**
 * Sayt bo'ylab yagona rasm ko'ruvchi — `openLightbox()` chaqirilganda ochiladi.
 *
 * Boshqaruv: Esc — yopish, ← → — suratlar orasida yurish, fonni bosish — yopish,
 * sensorli ekranda chapga/o'ngga surish. O'ng yuqorida yopish tugmasi,
 * chetlarda strelkalar, pastda «joriy/jami» hisoblagichi.
 */
import { onKeyStroke, useSwipe } from '@vueuse/core'
import { nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { useLightbox } from '@/composables/useLightbox'
import { useScrollLock } from '@/composables/useScrollLock'

const { t } = useI18n()
const { images, index, isOpen, current, step, close } = useLightbox()

const panel = ref(null)
const frame = ref(null)
const isLocked = useScrollLock()

/** Sensorli ekranda surish — 60px dan katta harakat suratni almashtiradi. */
useSwipe(frame, {
  threshold: 60,
  onSwipeEnd(_event, direction) {
    if (!isOpen.value) return
    if (direction === 'left') step(1)
    if (direction === 'right') step(-1)
  },
})

watch(isOpen, async (value) => {
  isLocked.value = value
  if (value) {
    await nextTick()
    panel.value?.focus()
  }
})

onKeyStroke('Escape', () => isOpen.value && close())
onKeyStroke('ArrowLeft', () => isOpen.value && step(-1))
onKeyStroke('ArrowRight', () => isOpen.value && step(1))
</script>

<template>
  <Teleport to="body">
    <Transition name="lightbox">
      <div
        v-if="isOpen && current"
        ref="panel"
        role="dialog"
        aria-modal="true"
        :aria-label="t('cards.lightboxView')"
        tabindex="-1"
        class="fixed inset-0 z-[70] bg-black/90 outline-none backdrop-blur-md"
        @click.self="close()"
      >
        <!-- Surat maydoni: chetlarda strelkalar uchun joy qoldiriladi -->
        <div
          ref="frame"
          class="flex h-full w-full items-center justify-center px-[4.5rem] py-20 sm:px-24 sm:py-24"
          @click.self="close()"
        >
          <Transition name="lightbox-image" mode="out-in">
            <figure :key="current.src" class="max-h-full">
              <img
                loading="lazy"
                decoding="async"
                :src="current.src"
                :alt="current.alt || ''"
                class="rounded-block mx-auto max-h-[78vh] w-auto max-w-full object-contain shadow-2xl"
              />
              <figcaption
                v-if="current.alt"
                class="text-small mx-auto mt-4 max-w-2xl text-center text-white/60"
              >
                {{ current.alt }}
              </figcaption>
            </figure>
          </Transition>
        </div>

        <!-- Yopish -->
        <button
          type="button"
          class="text-brand absolute top-4 right-4 grid size-12 place-items-center rounded-full bg-white/8 transition duration-200 hover:bg-white/16 sm:top-6 sm:right-6 sm:size-14"
          :aria-label="t('common.close')"
          @click="close()"
        >
          <svg class="size-5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path
              d="M5 5l10 10M15 5L5 15"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />
          </svg>
        </button>

        <template v-if="images.length > 1">
          <button
            type="button"
            class="text-brand absolute top-1/2 left-3 grid size-12 -translate-y-1/2 place-items-center rounded-full bg-white/8 transition duration-200 hover:bg-white/16 sm:left-6 sm:size-14"
            :aria-label="t('cards.lightboxPrev')"
            @click="step(-1)"
          >
            <svg class="size-5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                d="M11.5 4.5 6 10l5.5 5.5M6 10h9"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>

          <button
            type="button"
            class="text-brand absolute top-1/2 right-3 grid size-12 -translate-y-1/2 place-items-center rounded-full bg-white/8 transition duration-200 hover:bg-white/16 sm:right-6 sm:size-14"
            :aria-label="t('cards.lightboxNext')"
            @click="step(1)"
          >
            <svg class="size-5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                d="M8.5 4.5 14 10l-5.5 5.5M14 10H5"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>

          <!-- Hisoblagich: joriy surat to'q sariq, jami — xira -->
          <p
            class="font-wide absolute right-6 bottom-6 text-lg font-bold sm:right-10 sm:bottom-8 sm:text-2xl"
            aria-live="polite"
          >
            <span class="text-brand">{{ index + 1 }}</span>
            <span class="text-white/45">/{{ images.length }}</span>
          </p>
        </template>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.lightbox-enter-active,
.lightbox-leave-active {
  transition: opacity 0.22s ease;
}
.lightbox-enter-from,
.lightbox-leave-to {
  opacity: 0;
}

/* Surat almashganda yumshoq o'tish */
.lightbox-image-enter-active,
.lightbox-image-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}
.lightbox-image-enter-from,
.lightbox-image-leave-to {
  opacity: 0;
  transform: scale(0.98);
}
</style>
