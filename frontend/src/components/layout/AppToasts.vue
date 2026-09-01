<script setup>
import { useI18n } from 'vue-i18n'

import { useUiStore } from '@/stores/ui'

const { t } = useI18n()
const ui = useUiStore()
</script>

<template>
  <Teleport to="body">
    <div
      class="pointer-events-none fixed inset-x-4 bottom-4 z-[60] flex flex-col items-center gap-2 sm:right-6 sm:left-auto sm:items-end"
      role="status"
      aria-live="polite"
    >
      <TransitionGroup name="toast">
        <div
          v-for="toast in ui.toasts"
          :key="toast.id"
          class="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-card px-5 py-4 text-sm text-white shadow-lg"
          :class="toast.type === 'success' ? 'bg-surface' : 'bg-brand'"
        >
          <span class="flex-1">{{ toast.message }}</span>
          <button
            type="button"
            class="opacity-70 transition hover:opacity-100"
            :aria-label="t('common.close')"
            @click="ui.dismiss(toast.id)"
          >
            ✕
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
