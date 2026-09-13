<script setup>
/**
 * Bo'lim muharriri — o'ng tomondagi panel.
 *
 * Bo'limning matn maydonlari uch tilda, rasmlari, elementlari (kartochkalar)
 * va «saytda ko'rsatilsin» belgisi. Bosilgan maydon ochilganda ajratib
 * ko'rsatiladi. «Сохранить» — bitta PATCH, keyin sayt qayta yuklanadi.
 */
import { computed, ref, watch } from 'vue'

import { uploadImage } from '@/api/editor'
import { getLanguage } from '@/i18n/language'
import { useEditorStore } from '@/stores/editor'

const editor = useEditorStore()

const LANGS = ['ru', 'uz', 'en']
const LANG_LABEL = { ru: 'RU', uz: 'UZ', en: 'EN' }
const FIELD_LABEL = {
  eyebrow: 'Ярлык над заголовком',
  title: 'Заголовок',
  subtitle: 'Подзаголовок',
  text: 'Текст',
  note: 'Примечание',
  button_label: 'Кнопка — текст',
  button2_label: 'Кнопка 2 — текст',
  button_url: 'Кнопка — ссылка',
  button2_url: 'Кнопка 2 — ссылка',
  image: 'Картинка',
  image2: 'Картинка 2',
  value: 'Значение',
  label: 'Подпись',
  list: 'Список (по строке)',
  icon_name: 'Иконка (имя)',
  icon: 'Иконка (файл)',
  url: 'Ссылка',
}
const PLAIN = new Set(['button_url', 'button2_url', 'image', 'image2', 'icon_name', 'icon', 'url'])
const IMAGE = new Set(['image', 'image2', 'icon'])
const LONG = new Set(['text', 'note', 'list', 'subtitle', 'title'])

const lang = ref('ru')
const values = ref({})
const items = ref([])
const isPublished = ref(true)
const uploading = ref('')
const dirty = ref(false)
const uploadError = ref('')

// Yuklash cheklovi — serverdagi bilan bir xil (5 MB). Katta faylni umuman
// yubormaymiz: sahifa qotib qolmaydi va foydalanuvchi sababni darhol ko'radi.
const MAX_UPLOAD_MB = 5

const section = computed(() => editor.section)
const activeField = computed(() => editor.active?.field || null)

watch(
  section,
  (s) => {
    if (!s) return
    values.value = { ...s.values }
    items.value = s.items.map((it) => ({ ...it }))
    isPublished.value = s.is_published
    dirty.value = false
    // Sayt qaysi tilda ochiq — muharrir ham o'shanda boshlaydi.
    lang.value = LANGS.includes(getLanguage()) ? getLanguage() : 'ru'
  },
  { immediate: true },
)

function key(field, l = lang.value) {
  return PLAIN.has(field) ? field : `${field}_${l}`
}

function fieldLabel(field) {
  return FIELD_LABEL[field] || field
}

function markDirty() {
  dirty.value = true
}

async function pickImage(event, target, field) {
  const file = event.target.files?.[0]
  event.target.value = ''
  uploadError.value = ''
  if (!file) return
  if (!/^image\/(png|jpe?g|webp|gif)$/.test(file.type)) {
    uploadError.value = 'Только PNG, JPG, WEBP или GIF.'
    return
  }
  if (file.size > MAX_UPLOAD_MB * 1024 * 1024) {
    uploadError.value = `Файл ${(file.size / 1024 / 1024).toFixed(1)} МБ — максимум ${MAX_UPLOAD_MB} МБ.`
    return
  }
  uploading.value = `${target === values.value ? 'section' : items.value.indexOf(target)}:${field}`
  try {
    const { path, url } = await uploadImage(file)
    target[field] = path
    target[`${field}_url`] = url
    markDirty()
  } catch (e) {
    uploadError.value = e.response?.data?.detail || 'Не удалось загрузить.'
  } finally {
    uploading.value = ''
  }
}

function clearImage(target, field) {
  target[field] = ''
  target[`${field}_url`] = null
  markDirty()
}

function addItem() {
  items.value.push({ id: null, is_published: true })
  markDirty()
}

function removeItem(index) {
  items.value.splice(index, 1)
  markDirty()
}

function moveItem(index, delta) {
  const next = index + delta
  if (next < 0 || next >= items.value.length) return
  const [row] = items.value.splice(index, 1)
  items.value.splice(next, 0, row)
  markDirty()
}

async function save() {
  const payload = { values: {}, is_published: isPublished.value }
  for (const [k, v] of Object.entries(values.value)) {
    if (k.endsWith('_url')) continue
    payload.values[k] = v ?? ''
  }
  if (section.value.item_fields.length) {
    payload.items = items.value.map((it) => {
      const row = {}
      for (const [k, v] of Object.entries(it)) {
        if (k === 'id' || k.endsWith('_url')) continue
        row[k] = v ?? ''
      }
      return { id: it.id ?? null, values: row }
    })
  }
  await editor.save(payload)
  dirty.value = false
}

function close() {
  if (dirty.value && !window.confirm('Есть несохранённые изменения. Закрыть?')) return
  editor.close()
}
</script>

<template>
  <Teleport to="body">
    <aside
      v-if="editor.active"
      data-editor-ui
      class="fixed inset-y-0 right-0 z-[95] flex w-full max-w-[30rem] flex-col bg-white text-ink shadow-[-12px_0_40px_rgba(0,0,0,0.35)]"
    >
      <!-- Sarlavha -->
      <header class="flex items-start gap-3 border-b border-gray-200 px-5 py-4">
        <div class="min-w-0 flex-1">
          <h2 class="truncate font-bold">{{ section?.name || editor.active.key }}</h2>
          <p v-if="section?.hint" class="mt-1 text-xs leading-snug text-gray-500">{{ section.hint }}</p>
        </div>
        <button type="button" class="text-2xl leading-none text-gray-400 hover:text-ink" aria-label="Закрыть" @click="close">×</button>
      </header>

      <div v-if="editor.loading" class="p-5 text-gray-500">Загрузка…</div>
      <p v-else-if="editor.error && !section" class="p-5 text-red-600">{{ editor.error }}</p>

      <div v-else-if="section" class="flex-1 overflow-y-auto px-5 py-4">
        <!-- Til -->
        <div class="mb-4 flex gap-1 rounded-pill bg-gray-100 p-1">
          <button
            v-for="l in LANGS"
            :key="l"
            type="button"
            class="flex-1 rounded-pill py-1 text-sm font-semibold"
            :class="lang === l ? 'bg-ink text-white' : 'text-gray-600 hover:bg-gray-200'"
            @click="lang = l"
          >
            {{ LANG_LABEL[l] }}
          </button>
        </div>

        <!-- Ko'rinish -->
        <label v-if="section.hideable" class="mb-4 flex items-center gap-2 text-sm">
          <input v-model="isPublished" type="checkbox" @change="markDirty" />
          Показывать блок на сайте
        </label>

        <!-- Maydonlar -->
        <div v-for="field in section.fields" :key="field" class="mb-4" :class="{ 'rounded-xl bg-brand/10 p-2 -m-2 mb-2': field === activeField }">
          <label class="mb-1 block text-xs font-semibold tracking-wide text-gray-500 uppercase">
            {{ fieldLabel(field) }}<span v-if="!PLAIN.has(field)" class="ml-1 font-normal">· {{ LANG_LABEL[lang] }}</span>
          </label>

          <template v-if="IMAGE.has(field)">
            <div class="flex items-center gap-3">
              <img v-if="values[`${field}_url`]" :src="values[`${field}_url`]" class="h-16 w-24 rounded-lg object-cover" alt="" />
              <div v-else class="grid h-16 w-24 place-items-center rounded-lg bg-gray-100 text-xs text-gray-400">нет</div>
              <label class="cursor-pointer rounded-pill bg-ink px-3 py-1 text-sm text-white hover:bg-brand">
                {{ uploading === `section:${field}` ? 'Загрузка…' : 'Заменить' }}
                <input type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="sr-only" @change="pickImage($event, values, field)" />
              </label>
              <button v-if="values[field]" type="button" class="text-sm text-gray-500 hover:text-red-600" @click="clearImage(values, field)">Убрать</button>
            </div>
          </template>
          <textarea
            v-else-if="LONG.has(field)"
            v-model="values[key(field)]"
            rows="3"
            class="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            @input="markDirty"
          />
          <input
            v-else
            v-model="values[key(field)]"
            type="text"
            class="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            @input="markDirty"
          />
        </div>

        <!-- Elementlar -->
        <section v-if="section.item_fields.length" class="mt-6 border-t border-gray-200 pt-4">
          <div class="mb-2 flex items-center justify-between">
            <h3 class="font-bold">{{ section.item_name || 'Элементы' }} <span class="text-gray-400">({{ items.length }})</span></h3>
            <button type="button" class="rounded-pill bg-ink px-3 py-1 text-sm text-white hover:bg-brand" @click="addItem">+ Добавить</button>
          </div>

          <div v-for="(item, index) in items" :key="item.id ?? `new-${index}`" class="mb-3 rounded-2xl border border-gray-200 p-3">
            <div class="mb-2 flex items-center gap-2 text-xs text-gray-500">
              <span class="font-semibold">#{{ index + 1 }}</span>
              <button type="button" class="hover:text-ink" :disabled="index === 0" @click="moveItem(index, -1)">↑</button>
              <button type="button" class="hover:text-ink" :disabled="index === items.length - 1" @click="moveItem(index, 1)">↓</button>
              <label class="ml-auto flex items-center gap-1">
                <input v-model="item.is_published" type="checkbox" @change="markDirty" /> показывать
              </label>
              <button type="button" class="ml-2 hover:text-red-600" @click="removeItem(index)">удалить</button>
            </div>

            <div v-for="field in section.item_fields" :key="field" class="mb-2">
              <label class="mb-1 block text-[11px] font-semibold tracking-wide text-gray-500 uppercase">
                {{ fieldLabel(field) }}<span v-if="!PLAIN.has(field)" class="ml-1 font-normal">· {{ LANG_LABEL[lang] }}</span>
              </label>
              <template v-if="IMAGE.has(field)">
                <div class="flex items-center gap-2">
                  <img v-if="item[`${field}_url`]" :src="item[`${field}_url`]" class="h-10 w-14 rounded object-cover" alt="" />
                  <label class="cursor-pointer rounded-pill bg-gray-100 px-2 py-1 text-xs hover:bg-gray-200">
                    {{ uploading === `${index}:${field}` ? '…' : 'Файл' }}
                    <input type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="sr-only" @change="pickImage($event, item, field)" />
                  </label>
                  <button v-if="item[field]" type="button" class="text-xs text-gray-500 hover:text-red-600" @click="clearImage(item, field)">убрать</button>
                </div>
              </template>
              <textarea
                v-else-if="LONG.has(field)"
                v-model="item[key(field)]"
                rows="2"
                class="w-full rounded-lg border border-gray-300 px-2 py-1 text-sm focus:border-brand focus:outline-none"
                @input="markDirty"
              />
              <input
                v-else
                v-model="item[key(field)]"
                type="text"
                class="w-full rounded-lg border border-gray-300 px-2 py-1 text-sm focus:border-brand focus:outline-none"
                @input="markDirty"
              />
            </div>
          </div>
        </section>
      </div>

      <footer class="flex items-center gap-3 border-t border-gray-200 px-5 py-3">
        <button
          type="button"
          class="rounded-pill bg-brand px-5 py-2 font-bold text-white disabled:opacity-50"
          :disabled="editor.saving || !section"
          @click="save"
        >
          {{ editor.saving ? 'Сохраняю…' : 'Сохранить' }}
        </button>
        <span v-if="uploadError" class="text-sm text-red-600">{{ uploadError }}</span>
        <span v-else-if="editor.error" class="text-sm text-red-600">{{ editor.error }}</span>
        <span v-else-if="dirty" class="text-sm text-gray-500">есть изменения</span>
        <span v-else-if="section" class="text-sm text-green-600">сохранено</span>
      </footer>
    </aside>
  </Teleport>
</template>
