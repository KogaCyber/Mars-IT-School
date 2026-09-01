<script setup>
/**
 * «Откликнуться на вакансию» — o'ngdan chiqadigan ariza paneli.
 *
 * Tepada vakansiya nomi va yopish tugmasi, ostida forma kartochkasi:
 * ism, telefon, rezyume havolasi va fayl (PDF/DOC/DOCX/RTF, 5 MB gacha).
 * Ariza yuborilgach, o'sha kartochka «Заявка принята» holatiga o'tadi.
 */
import { onKeyStroke, useScrollLock } from '@vueuse/core'
import { nextTick, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { normalizeError } from '@/api/client'
import { submitVacancyApplication } from '@/api/vacancies'
import BaseFloatingInput from '@/components/base/BaseFloatingInput.vue'
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

// Sahifaning scroll konteyneri — `html`, shuning uchun qulf ham unga qo'yiladi.
const isLocked = useScrollLock(document.documentElement)

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
          :aria-label="`Откликнуться на вакансию: ${vacancy.title}`"
          tabindex="-1"
          class="drawer-panel bg-ink relative flex max-h-[92dvh] w-full flex-col justify-center overflow-hidden rounded-t-[2rem] sm:justify-start px-6 py-7 outline-none sm:h-full sm:max-h-none sm:max-w-[38rem] sm:rounded-none sm:px-10 sm:py-10"
        >
          <!-- Telefon versiyada pastdan chiqadigan panel uchun "tutqich" -->
          <span
            class="mx-auto mb-5 h-1 w-12 shrink-0 rounded-full bg-white/20 sm:hidden"
            aria-hidden="true"
          />

          <div class="flex items-start justify-between gap-6">
            <h2 class="font-wide text-2xl leading-tight font-bold text-white sm:text-3xl">
              {{ vacancy.title }}
            </h2>

            <button
              type="button"
              class="text-brand grid size-12 shrink-0 place-items-center rounded-full bg-white/8 transition hover:bg-white/16"
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

          <!-- Forma kartochkasi -->
          <div
            class="rounded-block mt-8 border border-white/8 bg-white/6 p-6 backdrop-blur-sm sm:p-8"
          >
            <!-- Yuborilgandan keyingi holat -->
            <div v-if="isSent" class="flex min-h-[13rem] flex-col justify-center">
              <h3 class="font-wide text-2xl font-bold text-white">
                {{ t('vacancies.sentTitle') }}
                <span class="text-brand">{{ t('vacancies.sentTitleAccent') }}</span>
              </h3>
              <p class="text-lead mt-4 leading-relaxed text-white/70">
                {{ t('vacancies.sentText') }}
              </p>
            </div>

            <template v-else>
              <h3 class="font-wide text-2xl leading-tight font-bold sm:text-[1.75rem]">
                <span class="text-brand block">{{ t('vacancies.drawerTitleAccent') }}</span>
                <span class="block text-white">{{ t('vacancies.drawerTitle') }}</span>
              </h3>

              <form class="mt-6 flex flex-col gap-1" novalidate @submit.prevent="onSubmit">
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
                <div class="pt-4">
                  <div
                    class="flex items-center justify-between gap-4 border-b border-white/15 pb-3"
                  >
                    <button
                      v-if="!resume"
                      type="button"
                      class="text-lead text-left text-white/55 transition hover:text-white"
                      @click="pickFile"
                    >
                      {{ t('vacancies.attachResume') }}
                    </button>

                    <!-- Tanlangan fayl yorlig'i -->
                    <span
                      v-else
                      class="bg-brand rounded-pill text-small flex max-w-full items-center gap-2 py-[0.45em] pr-[0.5em] pl-[1em] text-white"
                    >
                      <span class="truncate">{{ resume.name }}</span>
                      <button
                        type="button"
                        class="grid size-5 shrink-0 place-items-center rounded-full bg-black/25 transition hover:bg-black/45"
                        :aria-label="t('vacancies.removeFile')"
                        @click="removeFile"
                      >
                        <svg class="size-3" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                          <path
                            d="M5.5 5.5l9 9M14.5 5.5l-9 9"
                            stroke="currentColor"
                            stroke-width="2.2"
                            stroke-linecap="round"
                          />
                        </svg>
                      </button>
                    </span>

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
                  class="bg-brand hover:bg-brand-hover rounded-pill mt-7 w-full py-[1em] font-medium text-white transition disabled:opacity-60"
                  :disabled="isSubmitting"
                >
                  {{ isSubmitting ? t('common.sending') : t('vacancies.submit') }}
                </button>
              </form>
            </template>
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
