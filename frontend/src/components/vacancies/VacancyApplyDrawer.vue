<script setup>
/**
 * «Откликнуться на вакансию» — o'ngdan chiqadigan ariza paneli.
 *
 * Tepada vakansiya nomi va yopish tugmasi, ostida forma kartochkasi:
 * ism, telefon, rezyume havolasi va fayl (PDF/DOC/DOCX/RTF, 5 MB gacha).
 * Ariza yuborilgach, o'sha kartochka «Заявка принята» holatiga o'tadi.
 */
import { onKeyStroke } from '@vueuse/core'
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { normalizeError } from '@/api/client'
import { submitVacancyApplication } from '@/api/vacancies'
import BaseFloatingInput from '@/components/base/BaseFloatingInput.vue'
import { useScrollLock } from '@/composables/useScrollLock'
import { useUiStore } from '@/stores/ui'
import { formatPhone, isValidPhone, toPhonePayload } from '@/utils/format'

const props = defineProps({
  /** Ariza yuboriladigan vakansiya (`null` bo'lsa panel yopiq). */
  vacancy: { type: Object, default: null },
})

const open = defineModel('open', { type: Boolean, required: true })

const { t } = useI18n()
const ui = useUiStore()

const ALLOWED_RESUME_TYPES = ['.pdf', '.doc', '.docx', '.rtf']
const MAX_RESUME_SIZE = 5 * 1024 * 1024

const form = reactive({ full_name: '', phone: '', resume_url: '', website: '' })
const errors = reactive({ full_name: '', phone: '', resume_url: '', resume: '' })
const resume = ref(null)
const fileInput = ref(null)
const panel = ref(null)
const isSubmitting = ref(false)
const isSent = ref(false)

// Panel ochiq bo'lganda orqa fon skroll qilinmaydi.
const isLocked = useScrollLock()

function reset() {
  Object.assign(form, { full_name: '', phone: '', resume_url: '', website: '' })
  Object.assign(errors, { full_name: '', phone: '', resume_url: '', resume: '' })
  resume.value = null
  isSent.value = false
}

watch(open, async (value) => {
  isLocked.value = value
  if (value) {
    reset()
    await nextTick()
    panel.value?.focus()
  }
})

onKeyStroke('Escape', () => {
  if (open.value) open.value = false
})

/** Telefon maydoni yozilayotgan paytda +998 90 123 45 67 ko'rinishiga keladi. */
function onPhoneInput(value) {
  form.phone = value ? formatPhone(value) : ''
}

/** Tanlangan fayl haqida qisqa ma'lumot: «PDF · 240 KB». */
const resumeMeta = computed(() => {
  const file = resume.value
  if (!file) return ''

  const extension = file.name.includes('.') ? file.name.split('.').pop().toUpperCase() : ''
  const kilobytes = file.size / 1024
  const size =
    kilobytes >= 1024
      ? `${(kilobytes / 1024).toFixed(1)} MB`
      : `${Math.max(1, Math.round(kilobytes))} KB`

  return extension ? `${extension} · ${size}` : size
})

function pickFile() {
  fileInput.value?.click()
}

function onFileChange(event) {
  const file = event.target.files?.[0] || null
  errors.resume = ''

  if (file) {
    const name = file.name.toLowerCase()
    if (!ALLOWED_RESUME_TYPES.some((ext) => name.endsWith(ext))) {
      errors.resume = t('vacancies.errorFileType')
      resume.value = null
      return
    }
    if (file.size > MAX_RESUME_SIZE) {
      errors.resume = t('vacancies.errorFileSize')
      resume.value = null
      return
    }
  }
  resume.value = file
}

function removeFile() {
  resume.value = null
  errors.resume = ''
  if (fileInput.value) fileInput.value.value = ''
}

function validate() {
  errors.full_name = form.full_name.trim().length < 2 ? t('forms.errorName') : ''
  errors.phone = isValidPhone(form.phone) ? '' : t('forms.errorPhone')
  errors.resume_url =
    !form.resume_url || /^https?:\/\/.+\..+/.test(form.resume_url.trim())
      ? ''
      : t('vacancies.errorResumeUrl')
  return !errors.full_name && !errors.phone && !errors.resume_url && !errors.resume
}

async function onSubmit() {
  if (!validate() || isSubmitting.value || !props.vacancy) return

  isSubmitting.value = true
  try {
    await submitVacancyApplication({
      vacancy: props.vacancy.slug,
      full_name: form.full_name.trim(),
      phone: toPhonePayload(form.phone),
      resume_url: form.resume_url.trim(),
      resume: resume.value || undefined,
      website: form.website,
    })
    isSent.value = true
  } catch (err) {
    const apiError = normalizeError(err)
    if (apiError.errors) {
      Object.entries(apiError.errors).forEach(([field, messages]) => {
        if (field in errors) errors[field] = messages[0] || ''
      })
    }
    ui.notify(apiError.detail, 'error')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="open && vacancy"
        class="fixed inset-0 z-[65] flex items-end justify-end sm:items-stretch"
      >
        <!-- Fon: sahifa xiralashadi -->
        <div class="absolute inset-0 bg-black/55 backdrop-blur-sm" @click="open = false" />

        <div
          ref="panel"
          role="dialog"
          aria-modal="true"
          :aria-label="`${t('vacancies.apply')}: ${vacancy.title}`"
          tabindex="-1"
          class="drawer-panel bg-ink relative flex max-h-[92dvh] w-full flex-col overflow-hidden rounded-t-[2rem] px-6 py-4 outline-none sm:h-full sm:max-h-none sm:max-w-[38rem] sm:rounded-none sm:px-10 sm:py-10"
        >
          <!-- Telefon versiyada pastdan chiqadigan panel uchun "tutqich" -->
          <span
            class="mx-auto mb-3 h-1 w-12 shrink-0 rounded-full bg-white/20 sm:hidden"
            aria-hidden="true"
          />

          <div class="flex items-center justify-between gap-4 sm:items-start sm:gap-6">
            <h2 class="font-wide text-xl leading-tight font-bold text-white sm:text-3xl">
              {{ vacancy.title }}
            </h2>

            <button
              type="button"
              class="text-brand grid size-10 shrink-0 place-items-center rounded-full bg-white/8 transition hover:bg-white/16 sm:size-12"
              :aria-label="t('common.close')"
              @click="open = false"
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

          <!-- Yuborilgandan keyingi holat: panel o'rtasida kichik kartochka -->
          <div
            v-if="isSent"
            role="status"
            aria-live="polite"
            class="flex flex-1 items-center justify-center py-6"
          >
            <div
              class="success-card rounded-block w-full max-w-[24rem] border border-white/8 bg-white/6 p-7 text-center backdrop-blur-sm sm:p-8"
            >
              <span
                class="success-badge bg-brand/12 text-brand mx-auto grid size-16 place-items-center rounded-full"
                aria-hidden="true"
              >
                <svg class="size-8" viewBox="0 0 24 24" fill="none">
                  <path
                    class="success-check"
                    d="m6 12.4 4.2 4.1L18 7.4"
                    stroke="currentColor"
                    stroke-width="2.2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>

              <h3 class="font-wide mt-5 text-2xl font-bold text-white">
                {{ t('vacancies.sentTitle') }}
                <span class="text-brand">{{ t('vacancies.sentTitleAccent') }}</span>
              </h3>
              <p class="mt-3 leading-relaxed text-white/70">
                {{ t('vacancies.sentText') }}
              </p>
            </div>
          </div>

          <!-- Forma kartochkasi -->
          <div
            v-else
            class="rounded-block mt-5 border border-white/8 bg-white/6 p-5 backdrop-blur-sm sm:mt-8 sm:p-8"
          >
            <h3 class="font-wide text-xl leading-tight font-bold sm:text-[1.75rem]">
              <span class="text-brand block">{{ t('vacancies.drawerTitleAccent') }}</span>
              <span class="block text-white">{{ t('vacancies.drawerTitle') }}</span>
            </h3>

            <form class="mt-4 flex flex-col gap-1" novalidate @submit.prevent="onSubmit">
              <BaseFloatingInput
                v-model="form.full_name"
                :label="t('forms.firstName')"
                autocomplete="name"
                required
                :error="errors.full_name"
              />

              <BaseFloatingInput
                :model-value="form.phone"
                :label="t('forms.phone')"
                type="tel"
                inputmode="tel"
                autocomplete="tel"
                required
                :error="errors.phone"
                @update:model-value="onPhoneInput"
              />

              <BaseFloatingInput
                v-model="form.resume_url"
                :label="t('vacancies.resumeLink')"
                type="url"
                inputmode="url"
                :error="errors.resume_url"
              />

              <!-- Fayl biriktirish -->
              <div class="pt-3">
                <!-- Fayl tanlanmagan: boshqa maydonlarga o'xshash pastki chiziqli qator -->
                <div
                  v-if="!resume"
                  class="flex items-center justify-between gap-4 border-b border-white/15 pb-3"
                >
                  <button
                    type="button"
                    class="text-lead text-left text-white/55 transition hover:text-white"
                    @click="pickFile"
                  >
                    {{ t('vacancies.attachResume') }}
                  </button>

                  <button
                    type="button"
                    class="text-brand grid size-9 shrink-0 place-items-center rounded-full bg-white/8 transition hover:bg-white/16"
                    :aria-label="t('vacancies.attachFile')"
                    @click="pickFile"
                  >
                    <svg class="size-4.5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                      <path
                        d="M13.5 6.2 7.9 11.8a1.9 1.9 0 0 0 2.7 2.7l5.9-5.9a3.4 3.4 0 0 0-4.8-4.8l-6 6a4.9 4.9 0 0 0 6.9 6.9l4.6-4.6"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </button>
                </div>

                <!-- Tanlangan fayl: nomi, hajmi va o'chirish tugmasi -->
                <div
                  v-else
                  class="file-chip flex items-center gap-3 rounded-2xl border border-white/12 bg-white/[0.06] p-2.5"
                >
                  <span
                    class="bg-brand/15 text-brand grid size-10 shrink-0 place-items-center rounded-xl"
                    aria-hidden="true"
                  >
                    <svg class="size-5" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M11.5 2.5H6.5A1.5 1.5 0 0 0 5 4v12a1.5 1.5 0 0 0 1.5 1.5h7A1.5 1.5 0 0 0 15 16V6l-3.5-3.5Z"
                        stroke="currentColor"
                        stroke-width="1.4"
                        stroke-linejoin="round"
                      />
                      <path
                        d="M11.5 2.5V6H15"
                        stroke="currentColor"
                        stroke-width="1.4"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>

                  <span class="min-w-0 flex-1">
                    <span class="block truncate text-[0.92rem] text-white">{{ resume.name }}</span>
                    <span class="block text-[0.74rem] text-white/40">{{ resumeMeta }}</span>
                  </span>

                  <button
                    type="button"
                    class="grid size-8 shrink-0 place-items-center rounded-full text-white/45 transition hover:bg-white/10 hover:text-white"
                    :aria-label="t('vacancies.removeFile')"
                    @click="removeFile"
                  >
                    <svg class="size-4" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                      <path
                        d="M5.5 5.5l9 9M14.5 5.5l-9 9"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                </div>

                <p
                  class="mt-2 text-[0.78rem]"
                  :class="errors.resume ? 'text-brand' : 'text-white/35'"
                >
                  {{ errors.resume || t('vacancies.fileHint') }}
                </p>

                <input
                  ref="fileInput"
                  type="file"
                  accept=".pdf,.doc,.docx,.rtf"
                  class="hidden"
                  @change="onFileChange"
                />
              </div>

              <!-- Honeypot: botlar uchun -->
              <div class="hidden" aria-hidden="true">
                <input v-model="form.website" type="text" tabindex="-1" autocomplete="off" />
              </div>

              <button
                type="submit"
                class="bg-brand hover:bg-brand-hover rounded-pill mt-5 w-full py-[0.9em] font-medium text-white transition disabled:opacity-60 sm:mt-7 sm:py-[1em]"
                :disabled="isSubmitting"
              >
                {{ isSubmitting ? t('common.sending') : t('vacancies.submit') }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Panel ostidagi rangli nur — Figma'dagi to'q sariq/binafsha yorug'lik */
.drawer-panel::before {
  content: '';
  position: absolute;
  inset-inline: -10%;
  bottom: -20%;
  height: 55%;
  pointer-events: none;
  background:
    radial-gradient(50% 60% at 78% 70%, rgba(233, 73, 33, 0.45), transparent 70%),
    radial-gradient(45% 55% at 18% 85%, rgba(59, 47, 122, 0.5), transparent 72%);
  filter: blur(10px);
}

.drawer-panel > * {
  position: relative;
}

/* Fayl tanlanganda kartochka yumshoq paydo bo'ladi */
.file-chip {
  animation: chip-in 0.22s ease-out both;
}

@keyframes chip-in {
  from {
    opacity: 0;
    transform: translateY(0.35rem);
  }
}

@media (prefers-reduced-motion: reduce) {
  .file-chip {
    animation: none;
  }
}

/* «Ariza qabul qilindi» kartochkasi: pastdan ko'tarilib paydo bo'ladi,
   ichidagi belgi esa kattalashib chiziladi. */
.success-card {
  animation: success-in 0.42s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.success-badge {
  animation: badge-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) 0.12s both;
}

.success-check {
  stroke-dasharray: 26;
  stroke-dashoffset: 26;
  animation: check-draw 0.4s ease-out 0.3s forwards;
}

@keyframes success-in {
  from {
    opacity: 0;
    transform: translateY(1.25rem) scale(0.96);
  }
}

@keyframes badge-in {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
}

@keyframes check-draw {
  to {
    stroke-dashoffset: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .success-card,
  .success-badge {
    animation: none;
  }

  .success-check {
    stroke-dashoffset: 0;
    animation: none;
  }
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.25s ease;
}
.drawer-enter-active .drawer-panel,
.drawer-leave-active .drawer-panel {
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
/* Telefonda panel pastdan ko'tariladi */
.drawer-enter-from .drawer-panel,
.drawer-leave-to .drawer-panel {
  transform: translateY(100%);
}

/* Katta ekranda — o'ng chetdan sirg'aladi */
@media (min-width: 640px) {
  .drawer-enter-from .drawer-panel,
  .drawer-leave-to .drawer-panel {
    transform: translateX(6%);
  }
}
</style>
