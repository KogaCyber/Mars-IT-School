/** Interfeys holati: mobil menyu, ariza modali, ariza qabul qilindi paneli, bildirishnomalar. */
import { defineStore } from 'pinia'
import { ref } from 'vue'

let toastId = 0

export const useUiStore = defineStore('ui', () => {
  const isMobileMenuOpen = ref(false)
  const isLeadSuccessOpen = ref(false)
  const toasts = ref([])

  function toggleMobileMenu(value) {
    isMobileMenuOpen.value = value === undefined ? !isMobileMenuOpen.value : value
  }

  /** Ariza muvaffaqiyatli yuborilgandan keyingi panel (pastdan chiqadi). */
  function openLeadSuccess() {
    isLeadSuccessOpen.value = true
  }

  function closeLeadSuccess() {
    isLeadSuccessOpen.value = false
  }

  /** @param {'success'|'error'} type */
  function notify(message, type = 'success') {
    const id = ++toastId
    toasts.value.push({ id, type, message })
    setTimeout(() => dismiss(id), 5000)
  }

  function dismiss(id) {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  return {
    isMobileMenuOpen,
    isLeadSuccessOpen,
    toasts,
    toggleMobileMenu,
    openLeadSuccess,
    closeLeadSuccess,
    notify,
    dismiss,
  }
})
