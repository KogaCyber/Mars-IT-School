/**
 * Vizual muharrir holati.
 *
 * Xodim (Mars ID orqali kirgan) sahifada «Tahrirlash» rejimini yoqadi:
 * bo'lim matnlari va rasmlari ajratib ko'rsatiladi, bosilganda o'ng tomonda
 * o'sha bo'limning muharriri ochiladi. Saqlagach kontent qayta yuklanadi —
 * sahifa yangi matn bilan chiziladi.
 */
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { fetchMe, fetchPages, fetchSection, loginUrl, logout as apiLogout, patchSection } from '@/api/editor'

import { useContentStore } from './content'

const EDITING_KEY = 'mars.editing'

export const useEditorStore = defineStore('editor', () => {
  const user = ref(null)
  const checked = ref(false)
  const editing = ref(false)
  /** Ochiq bo'lim: { key, field } yoki null. */
  const active = ref(null)
  /** Ochiq bo'limning to'liq ma'lumoti (barcha tillar, elementlar). */
  const section = ref(null)
  const pages = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref('')

  const isEditor = computed(() => Boolean(user.value))

  async function init() {
    if (checked.value) return
    try {
      user.value = await fetchMe()
    } catch {
      user.value = null
    } finally {
      checked.value = true
    }
    if (user.value) {
      try {
        editing.value = sessionStorage.getItem(EDITING_KEY) === '1'
      } catch {
        /* sessionStorage bloklangan bo'lishi mumkin */
      }
      applyBodyClass()
      return
    }
    // Kirish nuqtasi ataylab ko'rinmas: `?edit=1` bilan kelgan (xodim) Mars ID'ga yo'naltiriladi.
    if (typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('edit')) {
      const url = new URL(window.location.href)
      url.searchParams.delete('edit')
      window.location.assign(loginUrl(url.pathname + url.search))
    }
  }

  function applyBodyClass() {
    if (typeof document === 'undefined') return
    document.body.classList.toggle('is-editing', editing.value && isEditor.value)
  }

  function setEditing(value) {
    editing.value = Boolean(value)
    if (!editing.value) close()
    try {
      sessionStorage.setItem(EDITING_KEY, editing.value ? '1' : '0')
    } catch {
      /* jim */
    }
    applyBodyClass()
  }

  async function loadPages() {
    if (pages.value.length) return pages.value
    pages.value = await fetchPages()
    return pages.value
  }

  async function open(key, field = null) {
    active.value = { key, field }
    loading.value = true
    error.value = ''
    try {
      section.value = await fetchSection(key)
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось загрузить блок.'
      section.value = null
    } finally {
      loading.value = false
    }
  }

  function close() {
    active.value = null
    section.value = null
    error.value = ''
  }

  /** Saqlaydi va saytni yangilaydi. `payload` — { values, is_published, items }. */
  async function save(payload) {
    if (!active.value) return
    saving.value = true
    error.value = ''
    try {
      section.value = await patchSection(active.value.key, payload)
      pages.value = [] // keyingi ochilishda qayta o'qiladi
      await useContentStore().load({ force: true })
    } catch (e) {
      error.value = e.response?.data?.detail || 'Не удалось сохранить.'
      throw e
    } finally {
      saving.value = false
    }
  }

  async function logout() {
    try {
      await apiLogout()
    } finally {
      user.value = null
      setEditing(false)
    }
  }

  return {
    user,
    checked,
    editing,
    active,
    section,
    pages,
    loading,
    saving,
    error,
    isEditor,
    init,
    setEditing,
    loadPages,
    open,
    close,
    save,
    logout,
  }
})
