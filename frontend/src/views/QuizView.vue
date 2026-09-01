<script setup>
/**
 * «Тест» — proforientatsiya testi.
 *
 * Maket: tepada yo'l yorliqlari va yirik sarlavha (test nomi), ostida bitta
 * katta to'q kartochka. Kartochka ikki ustunli: chapda salomlashish va izoh,
 * o'ngda progress chizig'i, savol, javob variantlari, «Назад» tugmasi va
 * «1/20» hisoblagichi. Kontakt bosqichi ham shu kartochka ichida ochiladi.
 */
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { normalizeError } from '@/api/client'
import { fetchQuiz, submitQuiz } from '@/api/quiz'
import BaseBreadcrumbs from '@/components/base/BaseBreadcrumbs.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import { useAsyncData } from '@/composables/useAsyncData'
import { useSeo } from '@/composables/useSeo'
import { useUiStore } from '@/stores/ui'
import { formatPhone, isValidPhone, toPhonePayload } from '@/utils/format'

/** Testning slug'i — admin panelda shu nom bilan yaratiladi. */
const QUIZ_SLUG = 'proforientatsiya'

const { t } = useI18n()
const router = useRouter()
const ui = useUiStore()

useSeo(() => ({
  title: t('quiz.seoTitle'),
  description: t('quiz.seoDescription'),
  breadcrumbs: [
    { name: t('pages.breadcrumbHome'), path: '/' },
    { name: t('nav.quiz'), path: '/test' },
  ],
}))

const { data: quiz, isLoading, error } = useAsyncData(() => fetchQuiz(QUIZ_SLUG), null)

const answers = reactive({})
const step = ref(0)
const contact = reactive({ full_name: '', phone: '+998 ' })
const contactError = ref('')
const isSubmitting = ref(false)

const questions = computed(() => quiz.value?.questions || [])
const currentQuestion = computed(() => questions.value[step.value] || null)
const isContactStep = computed(
  () => questions.value.length > 0 && step.value >= questions.value.length,
)

/** Maketdagi sarlavha — admin paneldagi test nomi. */
const title = computed(() => quiz.value?.title || t('quiz.defaultTitle'))

/**
 * Progress: birinchi savolda ham chiziq boshida kichik nuqta ko'rinib turadi,
 * shuning uchun to'ldirish kamida 2% bo'ladi.
 */
const progress = computed(() => {
  if (!questions.value.length) return 0
  return Math.max(2, Math.round((step.value / questions.value.length) * 100))
})

/** Kontakt bosqichida kiritilgan ism salomlashuvda ko'rinadi. */
const greetingName = computed(() => contact.full_name.trim())

function choose(questionId, optionId) {
  answers[questionId] = optionId
  // Javob tanlangach avtomatik keyingi savolga o'tamiz.
  step.value += 1
}

function back() {
  if (step.value > 0) step.value -= 1
}

async function submit() {
  contactError.value =
    contact.phone.trim() && !isValidPhone(contact.phone) ? t('forms.errorPhone') : ''
  if (contactError.value || isSubmitting.value) return

  isSubmitting.value = true
  try {
    const result = await submitQuiz(QUIZ_SLUG, {
      answers: { ...answers },
      full_name: contact.full_name.trim(),
      phone: contact.phone.trim() ? toPhonePayload(contact.phone) : '',
    })
    router.push({ name: 'quiz-result', params: { id: result.id } })
  } catch (err) {
    ui.notify(normalizeError(err).detail, 'error')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <BaseSpinner v-if="isLoading" :label="t('quiz.loading')" />

  <div v-else-if="error || !quiz" class="section container-page">
    <BaseEmptyState :title="t('quiz.unavailable')" :description="error || ''" />
  </div>

  <section v-else class="bg-ink pt-[3%] pb-[var(--spacing-section)]">
    <div class="container-page">
      <BaseBreadcrumbs
        :items="[
          { label: t('pages.breadcrumbHome'), to: { name: 'home' } },
          { label: t('nav.quiz') },
        ]"
      />

      <h1 v-reveal class="title-quiz font-wide mt-[4%] font-bold text-white">{{ title }}</h1>

      <!-- Katta kartochka: chapda salomlashish, o'ngda savol -->
      <div
        v-reveal="{ delay: 120 }"
        class="bg-surface mt-[6%] grid gap-10 rounded-[2.5rem] p-7 sm:p-10 lg:grid-cols-[1fr_2.1fr] lg:gap-16 lg:p-14"
      >
        <!-- Chap ustun -->
        <div>
          <p class="font-wide text-[1.35rem] leading-tight font-bold">
            <span class="text-brand">{{ t('quiz.greeting') }}</span
            ><span class="text-white/40">,</span>
            <span class="mt-1 block text-white/40">
              {{ greetingName || t('quiz.greetingFallback') }}
            </span>
          </p>

          <p class="mt-6 max-w-[34ch] leading-relaxed text-white/55">
            {{ t('quiz.intro') }}
          </p>
        </div>

        <!-- O'ng ustun -->
        <div class="flex flex-col">
          <!-- Progress chizig'i -->
          <div
            class="h-1.5 overflow-hidden rounded-pill bg-white/10"
            role="progressbar"
            :aria-valuenow="progress"
            aria-valuemin="0"
            aria-valuemax="100"
          >
            <div
              class="bg-brand h-full rounded-pill transition-all duration-500"
              :style="{ width: `${progress}%` }"
            />
          </div>

          <!-- Savol bosqichi -->
          <template v-if="currentQuestion">
            <h2 class="font-wide mt-8 text-[1.15rem] leading-snug font-bold text-white">
              {{ currentQuestion.text }}
            </h2>

            <img
              loading="lazy"
              decoding="async"
              v-if="currentQuestion.image"
              :src="currentQuestion.image"
              alt=""
              aria-hidden="true"
              class="mt-6 w-full rounded-card object-cover"
            />

            <ul class="mt-7 flex flex-col gap-3.5">
              <li v-for="option in currentQuestion.options" :key="option.id">
                <button
                  type="button"
                  class="group bg-ink flex w-full items-center justify-between gap-6 rounded-[1.5rem] border px-6 py-5 text-left transition duration-300 hover:border-brand/60 lg:px-8"
                  :class="
                    answers[currentQuestion.id] === option.id
                      ? 'border-brand'
                      : 'border-transparent'
                  "
                  @click="choose(currentQuestion.id, option.id)"
                >
                  <span class="font-wide font-bold text-white">{{ option.text }}</span>

                  <span
                    class="text-brand grid size-9 shrink-0 place-items-center rounded-full bg-white/5 transition duration-300 group-hover:bg-brand group-hover:text-white"
                    aria-hidden="true"
                  >
                    <svg class="size-4" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M4 10h12m0 0-4.5-4.5M16 10l-4.5 4.5"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </span>
                </button>
              </li>
            </ul>

            <!-- Pastki qator: «Назад» va hisoblagich -->
            <div class="mt-9 flex items-center justify-between gap-4">
              <button
                type="button"
                class="press bg-brand rounded-pill px-10 py-4 transition duration-200 hover:translate-y-[-3px] disabled:opacity-40"
                :disabled="step === 0"
                @click="back"
              >
                {{ t('quiz.back') }}
              </button>

              <p class="font-wide text-[1.35rem] font-bold text-white/50" aria-live="polite">
                <span class="text-brand">{{ step + 1 }}</span
                >/{{ questions.length }}
              </p>
            </div>
          </template>

          <!-- Kontakt bosqichi -->
          <template v-else-if="isContactStep">
            <h2 class="font-wide mt-8 text-[1.15rem] leading-snug font-bold text-white">
              {{ t('quiz.almostDone') }}
            </h2>
            <p class="mt-3 leading-relaxed text-white/55">
              {{ t('quiz.contactText') }}
            </p>

            <div class="mt-7 flex flex-col gap-4">
              <BaseInput
                v-model="contact.full_name"
                :label="t('forms.firstName')"
                autocomplete="name"
              />
              <BaseInput
                :model-value="contact.phone"
                :label="t('forms.phone')"
                type="tel"
                autocomplete="tel"
                :error="contactError"
                @update:model-value="contact.phone = formatPhone($event)"
              />
            </div>

            <div class="mt-9 flex items-center justify-between gap-4">
              <button
                type="button"
                class="press bg-ink rounded-pill px-10 py-4 text-white/45 transition hover:text-white"
                @click="back"
              >
                {{ t('quiz.back') }}
              </button>

              <BaseButton
                size="lg"
                class="font-wide font-bold"
                :loading="isSubmitting"
                @click="submit"
              >
                {{ t('quiz.showResult') }}
              </BaseButton>
            </div>
          </template>

          <BaseEmptyState v-else :title="t('quiz.noQuestions')" class="mt-8" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* Maketda sarlavha sahifa sarlavhalaridan yirikroq */
.title-quiz {
  font-size: clamp(2.25rem, 5.2vw, 5.5rem);
  line-height: 1.03;
}
</style>
