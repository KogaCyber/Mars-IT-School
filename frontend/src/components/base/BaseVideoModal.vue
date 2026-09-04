<script setup>
/**
 * Sayt bo'ylab yagona video ko'ruvchi — `openVideo()` chaqirilganda ochiladi.
 *
 * Maqsad: foydalanuvchi videoni ko'rish uchun YouTube'ga o'tib ketmasin —
 * hammasi shu sahifaning o'zida, modal oyna ichida o'ynaydi.
 * Boshqaruv: Esc — yopish, fonni bosish — yopish.
 */
import { onKeyStroke } from '@vueuse/core'
import { nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { useScrollLock } from '@/composables/useScrollLock'
import { useVideoModal } from '@/composables/useVideoModal'

const { t } = useI18n()
const { isOpen, title, video, close } = useVideoModal()

const panel = ref(null)
const isLocked = useScrollLock()

watch(isOpen, async (value) => {
  isLocked.value = value
  if (value) {
    await nextTick()
    panel.value?.focus()
  }
})

onKeyStroke('Escape', () => isOpen.value && close())
</script>

<template>
  <Teleport to="body">
    <Transition name="video-modal">
      <div
        v-if="isOpen && video"
        ref="panel"
        role="dialog"
        aria-modal="true"
        :aria-label="title || t('common.videoPlayer')"
        tabindex="-1"
        class="fixed inset-0 z-[80] grid place-items-center bg-black/92 p-4 outline-none backdrop-blur-md sm:p-8"
        @click.self="close()"
      >
        <div class="w-full max-w-[68rem]" @click.self="close()">
          <div
            class="rounded-block relative aspect-video w-full overflow-hidden bg-black shadow-2xl"
          >
            <iframe
              v-if="video.kind === 'embed'"
              :src="video.src"
              :title="title || t('common.videoPlayer')"
              class="size-full"
              frameborder="0"
              allow="
                accelerometer;
                autoplay;
                clipboard-write;
                encrypted-media;
                gyroscope;
                picture-in-picture;
                web-share;
              "
              referrerpolicy="strict-origin-when-cross-origin"
              allowfullscreen
            />

            <video v-else :src="video.src" class="size-full" controls autoplay playsinline />
          </div>

          <p v-if="title" class="text-small mt-4 text-center text-white/60">{{ title }}</p>
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
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.video-modal-enter-active,
.video-modal-leave-active {
  transition: opacity 0.24s ease;
}
.video-modal-enter-from,
.video-modal-leave-to {
  opacity: 0;
}

.video-modal-enter-active .rounded-block {
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}
.video-modal-enter-from .rounded-block {
  transform: scale(0.94);
}
</style>
