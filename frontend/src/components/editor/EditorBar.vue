<script setup>
/**
 * Xodim uchun pastki panel: «Tahrirlash» rejimi, sahifa bo'limlari ro'yxati,
 * chiqish. Oddiy tashrifchi buni ko'rmaydi (`editor.isEditor`).
 */
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { useEditorStore } from '@/stores/editor'

const editor = useEditorStore()
const route = useRoute()
const listOpen = ref(false)

/** Joriy sahifaning bo'limlari + umumiy bloklar (podval, tugmalar). */
const currentSections = computed(() => {
  if (!editor.pages.length) return []
  const path = route.path.replace(/\/$/, '') || '/'
  const page = editor.pages.find((p) => (p.url || '/').replace(/\/$/, '') === path)
  const common = editor.pages.find((p) => p.key === 'common')
  return [...(page?.sections ?? []), ...(common?.sections ?? [])]
})

watch(listOpen, async (open) => {
  if (open) await editor.loadPages()
})

function pick(section) {
  listOpen.value = false
  editor.open(section.key)
}
</script>

<template>
  <div
    v-if="editor.isEditor"
    data-editor-ui
    class="fixed bottom-4 left-4 z-[90] flex items-center gap-2 rounded-pill bg-white/95 px-3 py-2 text-sm text-ink shadow-[0_8px_30px_rgba(0,0,0,0.35)] backdrop-blur"
  >
    <span class="font-bold">{{ editor.user.name }}</span>

    <label class="ml-2 flex cursor-pointer items-center gap-2 select-none">
      <input
        type="checkbox"
        class="peer sr-only"
        :checked="editor.editing"
        @change="editor.setEditing($event.target.checked)"
      />
      <span
        class="relative h-6 w-11 rounded-full bg-gray-300 transition peer-checked:bg-brand after:absolute after:top-0.5 after:left-0.5 after:h-5 after:w-5 after:rounded-full after:bg-white after:transition peer-checked:after:translate-x-5"
      />
      <span>Режим правки</span>
    </label>

    <button
      v-if="editor.editing"
      type="button"
      class="rounded-pill bg-ink px-3 py-1 text-white hover:bg-brand"
      @click="editor.showContent = true"
    >
      Контент
    </button>

    <div v-if="editor.editing" class="relative">
      <button
        type="button"
        class="rounded-pill bg-ink px-3 py-1 text-white hover:bg-brand"
        @click="listOpen = !listOpen"
      >
        Блоки страницы
      </button>
      <ul
        v-if="listOpen"
        class="absolute bottom-full left-0 mb-2 max-h-[60vh] w-80 overflow-auto rounded-2xl bg-white p-2 shadow-[0_8px_30px_rgba(0,0,0,0.35)]"
      >
        <li v-if="!currentSections.length" class="px-3 py-2 text-gray-500">Загрузка…</li>
        <li v-for="s in currentSections" :key="s.key">
          <button
            type="button"
            class="w-full rounded-xl px-3 py-2 text-left hover:bg-gray-100"
            :class="{ 'opacity-50': !s.is_published }"
            @click="pick(s)"
          >
            <span class="block font-semibold">{{ s.name }}</span>
            <span class="block text-xs text-gray-500">{{ s.key }}</span>
          </button>
        </li>
      </ul>
    </div>

    <button type="button" class="ml-2 text-gray-500 hover:text-brand" @click="editor.logout()">
      Выйти
    </button>
  </div>
</template>
