<script setup>
/**
 * Ariza formasi — saytdagi barcha formalar shu komponentdan foydalanadi.
 * Xavfsizlik: honeypot maydoni + serverda so'rovlar cheklovi (5 ta / soat).
 */
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { normalizeError } from '@/api/client'
import { submitLead } from '@/api/leads'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseTextarea from '@/components/base/BaseTextarea.vue'
import { courseApiSlug } from '@/data/courseAliases'
import { useUiStore } from '@/stores/ui'
import { formatPhone, isValidPhone, toPhonePayload } from '@/utils/format'

const { t } = useI18n()

const props = defineProps({
  source: { type: String, default: 'home' },
  courseSlug: { type: String, default: null },
  branchSlug: { type: String, default: null },
  withComment: { type: Boolean, default: false },
  withChildAge: { type: Boolean, default: false },
  /** Bo'sh qoldirilsa — «Ariza qoldirish» tarjimasi ishlatiladi. */
  submitLabel: { type: String, default: '' },
  /** Maydonlar ko'rinishi: `pill` (standart) yoki `line` (pastki chiziqli). */
  variant: { type: String, default: 'pill' },
  /** Ism va familiya alohida maydonlarga ajratilsinmi. */
  splitName: { type: Boolean, default: false },
  /** Shaxsiy ma'lumotlar haqidagi izoh ko'rsatilsinmi. */
  withConsentNote: { type: Boolean, default: true },
})

const emit = defineEmits(['submitted'])

const ui = useUiStore()

const form = reactive({
  first_name: '',
  last_name: '',
  full_name: '',
  phone: '+998 ',
  child_age: '',
  comment: '',
  website: '',
})
const errors = reactive({ full_name: '', phone: '', child_age: '' })

/** Backend bitta `full_name` kutadi — ajratilgan maydonlar shu yerda birlashadi. */
const fullName = computed(() =>
  props.splitName
    ? `${form.first_name.trim()} ${form.last_name.trim()}`.trim()
    : form.full_name.trim(),
)
const isSubmitting = ref(false)

const submitText = computed(() => props.submitLabel || t('forms.submit'))

function onPhoneInput(value) {
  form.phone = formatPhone(value)
}

function validate() {
  errors.full_name = fullName.value.length < 2 ? t('forms.errorName') : ''
  errors.phone = isValidPhone(form.phone) ? '' : t('forms.errorPhone')

  const age = Number(form.child_age)
  errors.child_age =
    props.withChildAge && form.child_age && (Number.isNaN(age) || age < 3 || age > 25)
      ? t('forms.errorAge')
      : ''

  return !errors.full_name && !errors.phone && !errors.child_age
}

async function onSubmit() {
  if (!validate() || isSubmitting.value) return

  isSubmitting.value = true
  try {
    await submitLead({
      full_name: fullName.value,
      phone: toPhonePayload(form.phone),
      course: courseApiSlug(props.courseSlug),
      branch: props.branchSlug,
      child_age: props.withChildAge && form.child_age ? Number(form.child_age) : null,
      comment: props.withComment ? form.comment.trim() : '',
      source: props.source,
      website: form.website,
    })
    ui.openLeadSuccess()
    form.first_name = ''
    form.last_name = ''
    form.full_name = ''
    form.phone = '+998 '
    form.child_age = ''
    form.comment = ''
    emit('submitted')
  } catch (error) {
    const apiError = normalizeError(error)
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
  <form class="flex flex-col gap-4" novalidate @submit.prevent="onSubmit">
    <template v-if="splitName">
      <BaseInput
        v-model="form.first_name"
        :label="t('forms.firstName')"
        :variant="variant"
        :placeholder="variant === 'line' ? '' : t('forms.firstNamePlaceholder')"
        autocomplete="given-name"
        required
        :error="errors.full_name"
      />

      <BaseInput
        v-model="form.last_name"
        :label="t('forms.lastName')"
        :variant="variant"
        :placeholder="variant === 'line' ? '' : t('forms.lastNamePlaceholder')"
        autocomplete="family-name"
      />
    </template>

    <BaseInput
      v-else
      v-model="form.full_name"
      :label="t('forms.fullName')"
      :variant="variant"
      :placeholder="variant === 'line' ? '' : t('forms.fullNamePlaceholder')"
      autocomplete="name"
      required
      :error="errors.full_name"
    />

    <BaseInput
      :model-value="form.phone"
      :label="t('forms.phone')"
      type="tel"
      :variant="variant"
      :placeholder="variant === 'line' ? '' : t('forms.phonePlaceholder')"
      autocomplete="tel"
      required
      :error="errors.phone"
      @update:model-value="onPhoneInput"
    />

    <BaseInput
      v-if="withChildAge"
      v-model="form.child_age"
      :label="t('forms.childAge')"
      type="number"
      :variant="variant"
      :placeholder="variant === 'line' ? '' : t('forms.childAgePlaceholder')"
      :error="errors.child_age"
    />

    <BaseTextarea
      v-if="withComment"
      v-model="form.comment"
      :label="t('forms.comment')"
      :placeholder="t('forms.commentPlaceholder')"
      :rows="3"
    />

    <!-- Honeypot: ekranda ko'rinmaydi, faqat botlar to'ldiradi. -->
    <div class="hidden" aria-hidden="true">
      <label for="website">Website</label>
      <input id="website" v-model="form.website" type="text" tabindex="-1" autocomplete="off" />
    </div>

    <BaseButton
      type="submit"
      size="lg"
      block
      :loading="isSubmitting"
      :class="variant === 'line' ? 'font-wide mt-[4%] h-[3.5rem] font-bold' : ''"
    >
      {{ submitText }}
    </BaseButton>

    <p v-if="withConsentNote" class="text-muted text-center text-sm">
      {{ t('forms.consentNote') }}
    </p>
  </form>
</template>
