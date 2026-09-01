<script setup>
/**
 * «Заявка принята» paneli — ariza yuborilgandan keyin ekranning **pastidan**
 * sirg'alib chiqadigan varaq (Figma). Sahifaning qolgan qismi ochiq va o'qiladi
 * qoladi: panel yarim shaffof va faqat **o'z ortidagi** kontentni xiralashtiradi.
 *
 * Escape yoki o'ngdagi tugma bilan yopiladi.
 */
import { onKeyStroke } from '@vueuse/core'
import { nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { useUiStore } from '@/stores/ui'

const { t } = useI18n()
const ui = useUiStore()

const panel = ref(null)

onKeyStroke('Escape', () => {
  if (ui.isLeadSuccessOpen) ui.closeLeadSuccess()
})

watch(
  () => ui.isLeadSuccessOpen,
  async (isOpen) => {
    if (!isOpen) return
    await nextTick()
    panel.value?.focus()
  },
)
</script>

<template>
  <Teleport to="body">
    <Transition name="sheet">
      <section
        v-if="ui.isLeadSuccessOpen"
        ref="panel"
        role="status"
        aria-live="polite"
        tabindex="-1"
        class="fixed inset-x-0 bottom-0 z-[70] border-t border-white/10 bg-white/[0.07] px-0 pt-[var(--spacing-block)] pb-[var(--spacing-block)] outline-none backdrop-blur-2xl [border-radius:var(--radius-block)_var(--radius-block)_0_0]"
      >
        <div class="container-page flex items-start gap-4 sm:gap-8">
          <div class="min-w-0 flex-1 sm:mx-auto sm:max-w-[46rem]">
            <h2 class="section-title font-wide font-bold text-white">
              {{ t('forms.successTitle') }}
              <span class="text-brand">{{ t('forms.successTitleAccent') }}</span>
            </h2>

            <p class="text-lead mt-[1.1em] leading-relaxed text-white/85">
              {{ t('forms.successText') }}
              <br />
              {{ t('forms.successTextSecond') }}
            </p>
          </div>

          <button
            type="button"
            class="bg-surface-2/80 text-brand grid size-11 shrink-0 place-items-center rounded-full transition hover:bg-white/20 sm:size-14"
            :aria-label="t('common.close')"
            @click="ui.closeLeadSuccess()"
          >
            <svg class="size-5 sm:size-6" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                d="M5 5l10 10M15 5L5 15"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>
      </section>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Pastdan sirg'alib chiqadi va shu yo'l bilan qaytadi */
.sheet-enter-active,
.sheet-leave-active {
  transition:
    transform 0.4s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.25s ease;
}

.sheet-enter-from,
.sheet-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .sheet-enter-active,
  .sheet-leave-active {
    transition: opacity 0.2s ease;
  }

  .sheet-enter-from,
  .sheet-leave-to {
    transform: none;
  }
}
</style>
