<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  /** Bo'sh qoldirilsa — «Yuklanmoqda…» tarjimasi ishlatiladi. */
  label: { type: String, default: '' },
})

const labelText = computed(() => props.label || t('common.loading'))
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3 py-20" role="status">
    <span
      class="size-8 animate-spin rounded-full border-2 border-line border-t-brand"
      aria-hidden="true"
    />
    <span class="text-sm text-muted">{{ labelText }}</span>
  </div>
</template>
