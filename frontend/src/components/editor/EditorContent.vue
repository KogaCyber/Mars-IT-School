<script setup>
/**
 * «Контент» — alohida yozuvlarni boshqarish: kontaktlar, filiallar, yangiliklar,
 * vakansiyalar. Bo'limlar (matn bloklari) EditorPanel'da; bu yerda esa
 * qo'shish / o'zgartirish / o'chirish.
 *
 * Ko'rinish: chapda bo'limlar, o'ngda KARTOCHKALAR to'ri (rasm + nom + holat).
 * Kartochkaga bosilganda o'sha yozuv formasi ochiladi. Kontaktlar — bitta
 * yozuv, shuning uchun darhol forma.
 */
import { computed, ref } from 'vue'

import {
  createEntity,
  deleteEntity,
  fetchEntities,
  fetchSettings,
  patchSettings,
  updateEntity,
  uploadImage,
} from '@/api/editor'
import { getLanguage } from '@/i18n/language'
import { useContentStore } from '@/stores/content'
import { useEditorStore } from '@/stores/editor'
import { useLiveStore } from '@/stores/live'

/** Saqlagach sahifadagi ro'yxatlarni darhol yangilaydi — F5 kutilmasin. */
async function refreshPage() {
  await useContentStore().load({ force: true })
  useLiveStore().notify()
}

const editor = useEditorStore()

const TABS = [
  { kind: 'settings', title: 'Контакты' },
  { kind: 'branch', title: 'Филиалы' },
  { kind: 'news', title: 'Новости' },
  { kind: 'vacancy', title: 'Вакансии' },
]
const LANGS = ['ru', 'uz', 'en']
const LANG_LABEL = { ru: 'RU', uz: 'UZ', en: 'EN' }
const MAX_MB = 5
const PLAIN = new Set(['button_url', 'button2_url', 'image', 'image2', 'icon_name', 'icon', 'url'])

const active = ref('settings')
const fields = ref([])
const items = ref([])
const singular = ref('')
const editing = ref(null) // редактируемая запись или null (тогда — сетка карточек)
const isNew = ref(false)
const lang = ref('ru')
const busy = ref(false)
const error = ref('')

const isSettings = computed(() => active.value === 'settings')
const coverField = computed(() => fields.value.find((f) => f.kind === 'image'))

async function loadTab(kind) {
  active.value = kind
  editing.value = null
  isNew.value = false
  error.value = ''
  busy.value = true
  lang.value = LANGS.includes(getLanguage()) ? getLanguage() : 'ru'
  try {
    if (kind === 'settings') {
      const data = await fetchSettings()
      fields.value = data.fields
      editing.value = { ...data.values } // настройки — сразу форма
      singular.value = 'Контакты'
      items.value = []
    } else {
      const data = await fetchEntities(kind)
      fields.value = data.fields
      items.value = data.items
      singular.value = data.singular
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось загрузить.'
  } finally {
    busy.value = false
  }
}

function fieldKey(f, l = lang.value) {
  return f.kind === 'translated' ? `${f.name}_${l}` : f.name
}

function displayName(item) {
  const f = fields.value.find((x) => x.kind === 'translated') || fields.value[0]
  return (f && item[fieldKey(f, 'ru')]) || item.slug || `#${item.id}`
}

function cardCover(item) {
  return coverField.value ? item[`${coverField.value.name}_url`] : null
}

function cardSubtitle(item) {
  // Вторая строка карточки: краткое описание / адрес, если есть.
  const second = fields.value.find(
    (f) => f.kind === 'translated' && f.name !== (fields.value.find((x) => x.kind === 'translated')?.name),
  )
  return second ? item[fieldKey(second, 'ru')] : ''
}

function startNew() {
  isNew.value = true
  const draft = { is_published: true }
  for (const f of fields.value) {
    if (f.kind === 'translated') LANGS.forEach((l) => (draft[`${f.name}_${l}`] = ''))
    else if (f.kind === 'bool') draft[f.name] = f.name === 'is_open'
    else if (f.kind === 'select') draft[f.name] = f.options?.[0]?.value ?? ''
    else draft[f.name] = ''
  }
  editing.value = draft
}

function edit(item) {
  isNew.value = false
  editing.value = { ...item }
}

function backToGrid() {
  editing.value = null
  isNew.value = false
  error.value = ''
}

async function pickImage(event, field) {
  const file = event.target.files?.[0]
  event.target.value = ''
  error.value = ''
  if (!file) return
  if (!/^image\/(png|jpe?g|webp|gif)$/.test(file.type)) {
    error.value = 'Только PNG, JPG, WEBP или GIF.'
    return
  }
  if (file.size > MAX_MB * 1024 * 1024) {
    error.value = `Файл ${(file.size / 1024 / 1024).toFixed(1)} МБ — максимум ${MAX_MB} МБ.`
    return
  }
  busy.value = true
  try {
    const { path, url } = await uploadImage(file, active.value === 'settings' ? 'promo' : active.value)
    editing.value[field.name] = path
    editing.value[`${field.name}_url`] = url
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось загрузить.'
  } finally {
    busy.value = false
  }
}

function clearImage(field) {
  editing.value[field.name] = ''
  editing.value[`${field.name}_url`] = null
}

async function save() {
  busy.value = true
  error.value = ''
  const values = {}
  for (const [k, v] of Object.entries(editing.value)) {
    if (k === 'id' || k === 'is_published' || k.endsWith('_url')) continue
    values[k] = v
  }
  try {
    if (isSettings.value) {
      await patchSettings(values)
    } else if (isNew.value) {
      await createEntity(active.value, values, editing.value.is_published)
      await loadTab(active.value) // назад к сетке с обновлённым списком
    } else {
      const updated = await updateEntity(active.value, editing.value.id, values, editing.value.is_published)
      const i = items.value.findIndex((x) => x.id === updated.id)
      if (i >= 0) items.value[i] = updated
      editing.value = null
    }
    await refreshPage()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось сохранить.'
  } finally {
    busy.value = false
  }
}

async function remove(item) {
  if (!window.confirm(`Удалить «${displayName(item)}»?`)) return
  busy.value = true
  try {
    await deleteEntity(active.value, item.id)
    items.value = items.value.filter((x) => x.id !== item.id)
    await refreshPage()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось удалить.'
  } finally {
    busy.value = false
  }
}

loadTab('settings')
</script>

<template>
  <Teleport to="body">
    <div
      data-editor-ui
      class="fixed inset-0 z-[96] flex items-center justify-center bg-black/50 p-4"
      @click.self="editor.showContent = false"
    >
      <div class="flex h-[85vh] w-full max-w-5xl overflow-hidden rounded-3xl bg-white text-ink shadow-2xl">
        <!-- Разделы -->
        <nav class="w-44 shrink-0 border-r border-gray-200 bg-gray-50 p-3">
          <h2 class="mb-3 px-2 font-bold">Контент</h2>
          <button
            v-for="t in TABS"
            :key="t.kind"
            type="button"
            class="mb-1 w-full rounded-xl px-3 py-2 text-left text-sm"
            :class="active === t.kind ? 'bg-ink font-semibold text-white' : 'hover:bg-gray-200'"
            @click="loadTab(t.kind)"
          >
            {{ t.title }}
          </button>
          <button type="button" class="mt-4 w-full px-2 text-left text-sm text-gray-500 hover:text-ink" @click="editor.showContent = false">
            ← Закрыть
          </button>
        </nav>

        <div class="flex-1 overflow-y-auto">
          <!-- СЕТКА КАРТОЧЕК (для сущностей, когда ничего не выбрано) -->
          <div v-if="!isSettings && !editing" class="p-5">
            <p v-if="busy" class="text-gray-500">Загрузка…</p>
            <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3">
              <!-- Карточка «Добавить» -->
              <button
                type="button"
                class="flex aspect-[4/3] flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed border-gray-300 text-gray-500 transition hover:border-brand hover:text-brand"
                @click="startNew"
              >
                <span class="text-3xl">+</span>
                <span class="text-sm font-semibold">Добавить</span>
              </button>

              <!-- Карточки записей -->
              <div
                v-for="item in items"
                :key="item.id"
                class="group relative flex flex-col overflow-hidden rounded-2xl border border-gray-200 text-left transition hover:shadow-lg"
                :class="{ 'opacity-60': !item.is_published }"
              >
                <button type="button" class="flex flex-1 flex-col text-left" @click="edit(item)">
                  <div class="aspect-[4/3] w-full bg-gray-100">
                    <img v-if="cardCover(item)" :src="cardCover(item)" class="h-full w-full object-cover" alt="" />
                    <div v-else class="grid h-full place-items-center text-xs text-gray-400">без фото</div>
                  </div>
                  <div class="flex-1 p-3">
                    <p class="line-clamp-2 font-semibold">{{ displayName(item) }}</p>
                    <p v-if="cardSubtitle(item)" class="mt-1 line-clamp-2 text-xs text-gray-500">{{ cardSubtitle(item) }}</p>
                    <span v-if="!item.is_published" class="mt-2 inline-block rounded-pill bg-gray-200 px-2 py-0.5 text-[11px]">скрыто</span>
                  </div>
                </button>
                <button
                  type="button"
                  class="absolute top-2 right-2 grid h-7 w-7 place-items-center rounded-full bg-white/90 text-gray-500 opacity-0 shadow transition group-hover:opacity-100 hover:text-red-600"
                  title="Удалить"
                  @click.stop="remove(item)"
                >
                  ×
                </button>
              </div>
            </div>
          </div>

          <!-- ФОРМА (запись или контакты) -->
          <div v-else-if="editing" class="p-5">
            <div class="mb-4 flex items-center gap-2">
              <button v-if="!isSettings" type="button" class="text-sm text-gray-500 hover:text-ink" @click="backToGrid">← Назад</button>
              <h3 class="font-bold">{{ isSettings ? 'Контакты сайта' : isNew ? `Новая: ${singular}` : displayName(editing) }}</h3>
              <div class="ml-auto flex gap-1 rounded-pill bg-gray-100 p-1">
                <button
                  v-for="l in LANGS"
                  :key="l"
                  type="button"
                  class="rounded-pill px-3 py-1 text-sm font-semibold"
                  :class="lang === l ? 'bg-ink text-white' : 'text-gray-600'"
                  @click="lang = l"
                >
                  {{ LANG_LABEL[l] }}
                </button>
              </div>
            </div>

            <label v-if="!isSettings" class="mb-4 flex items-center gap-2 text-sm">
              <input v-model="editing.is_published" type="checkbox" />
              Показывать на сайте
            </label>

            <template v-for="(f, idx) in fields" :key="f.name">
              <h4
                v-if="f.group && f.group !== fields[idx - 1]?.group"
                class="mt-6 mb-3 border-b border-gray-100 pb-1 text-sm font-bold text-ink"
                :class="{ '!mt-0': idx === 0 }"
              >
                {{ f.group }}
              </h4>
              <div class="mb-4">
                <label class="mb-1 block text-xs font-semibold tracking-wide text-gray-500 uppercase">
                  {{ f.label }}<span v-if="f.kind === 'translated'" class="ml-1 font-normal">· {{ LANG_LABEL[lang] }}</span>
                </label>

                <template v-if="f.kind === 'image'">
                  <div class="flex items-center gap-3">
                    <img v-if="editing[`${f.name}_url`]" :src="editing[`${f.name}_url`]" class="h-20 w-28 rounded-lg object-cover" alt="" />
                    <div v-else class="grid h-20 w-28 place-items-center rounded-lg bg-gray-100 text-xs text-gray-400">нет</div>
                    <div class="flex flex-col gap-1">
                      <label class="cursor-pointer rounded-pill bg-ink px-3 py-1 text-center text-sm text-white hover:bg-brand">
                        {{ editing[`${f.name}_url`] ? 'Заменить' : 'Загрузить' }}
                        <input type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="sr-only" @change="pickImage($event, f)" />
                      </label>
                      <button v-if="editing[f.name]" type="button" class="text-xs text-gray-500 hover:text-red-600" @click="clearImage(f)">Убрать</button>
                      <span class="text-xs text-gray-400">до {{ MAX_MB }} МБ</span>
                    </div>
                  </div>
                </template>
                <select v-else-if="f.kind === 'select'" v-model="editing[f.name]" class="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm">
                  <option v-for="o in f.options" :key="o.value" :value="o.value">{{ o.label }}</option>
                </select>
                <label v-else-if="f.kind === 'bool'" class="flex items-center gap-2 text-sm">
                  <input v-model="editing[f.name]" type="checkbox" /> да
                </label>
                <input v-else-if="f.kind === 'number'" v-model="editing[f.name]" type="number" class="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm" />
                <textarea v-else-if="f.long || (f.kind === 'translated' && !PLAIN.has(f.name))" v-model="editing[fieldKey(f)]" rows="3" class="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm" />
                <input v-else v-model="editing[fieldKey(f)]" type="text" class="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm" />
              </div>
            </template>

            <div class="sticky bottom-0 -mx-5 flex items-center gap-3 border-t border-gray-200 bg-white px-5 py-3">
              <button type="button" class="rounded-pill bg-brand px-5 py-2 font-bold text-white disabled:opacity-50" :disabled="busy" @click="save">
                {{ busy ? 'Сохраняю…' : 'Сохранить' }}
              </button>
              <span v-if="error" class="text-sm text-red-600">{{ error }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
