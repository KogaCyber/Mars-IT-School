<script setup>
/**
 * Xodim uchun pastki panel: «Tahrirlash» rejimi, «Контент», chiqish.
 * Oddiy tashrifchi buni ko'rmaydi (`editor.isEditor`).
 *
 * «Блоки страницы» ro'yxati OLIB TASHLANDI: tahrirlash rejimida bo'limga
 * bevosita bosish o'sha bo'lim muharririni ochadi — ro'yxat ortiqcha edi.
 */
import { ref } from 'vue'

import { useEditorStore } from '@/stores/editor'

const editor = useEditorStore()
const showHint = ref(true)
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

    <button type="button" class="ml-2 text-gray-500 hover:text-brand" @click="editor.logout()">Выйти</button>
  </div>

  <!-- Tahrirlash rejimida qisqa ko'rsatma (bosib yopiladi). -->
  <div
    v-if="editor.isEditor && editor.editing && showHint"
    data-editor-ui
    class="fixed bottom-20 left-4 z-[90] max-w-xs rounded-2xl bg-ink/95 px-4 py-3 text-sm leading-snug text-white shadow-lg"
  >
    Нажмите на текст или картинку на странице, чтобы отредактировать. Курсы, филиалы,
    новости, вакансии и контакты — в кнопке «Контент».
    <button type="button" class="mt-2 block font-semibold text-brand" @click="showHint = false">Понятно</button>
  </div>
</template>
