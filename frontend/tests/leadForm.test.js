// @vitest-environment happy-dom
/**
 * `LeadForm` — saytdagi yagona ariza formasi va asosiy konversiya nuqtasi.
 *
 * Bu komponent sinalmagan edi, holbuki undagi xatolik to'g'ridan-to'g'ri
 * yo'qotilgan mijoz degani: forma jimgina yuborilmasa yoki telefon raqam
 * noto'g'ri formatda ketsa, buni hech qanday test ushlamasdi.
 */
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createI18n } from 'vue-i18n'

import LeadForm from '@/components/forms/LeadForm.vue'
import forms from '@/i18n/messages/forms.js'

const submitLead = vi.fn()
vi.mock('@/api/leads', () => ({ submitLead: (...args) => submitLead(...args) }))

const notify = vi.fn()
const openLeadSuccess = vi.fn()
vi.mock('@/stores/ui', () => ({
  useUiStore: () => ({ notify, openLeadSuccess }),
}))

const i18n = createI18n({
  legacy: false,
  locale: 'uz',
  fallbackLocale: 'uz',
  missingWarn: false,
  fallbackWarn: false,
  messages: { uz: { forms: forms.uz } },
})

function mountForm(props = {}) {
  return mount(LeadForm, {
    props,
    global: { plugins: [i18n] },
  })
}

/** Maydonlarni ekrandagi yorlig'i bo'yicha topadi — foydalanuvchi ko'rgani kabi. */
function inputByLabel(wrapper, label) {
  const field = wrapper
    .findAll('label')
    .find((node) => node.text().replace('*', '').trim() === label)
  const input = wrapper.find(`#${field.attributes('for')}`)
  return input
}

describe('LeadForm', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    submitLead.mockReset().mockResolvedValue('ok')
    notify.mockReset()
    openLeadSuccess.mockReset()
  })

  it("bo'sh forma yuborilmaydi va xato ko'rsatiladi", async () => {
    const wrapper = mountForm()
    await wrapper.find('form').trigger('submit')

    expect(submitLead).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain(forms.uz.errorName)
    expect(wrapper.text()).toContain(forms.uz.errorPhone)
  })

  it('to\'liq forma serverga tozalangan raqam bilan ketadi', async () => {
    const wrapper = mountForm({ source: 'courses' })

    await inputByLabel(wrapper, forms.uz.fullName).setValue('  Ali   Valiyev  ')
    await inputByLabel(wrapper, forms.uz.phone).setValue('+998 90 123 45 67')
    await wrapper.find('form').trigger('submit')

    expect(submitLead).toHaveBeenCalledTimes(1)
    expect(submitLead.mock.calls[0][0]).toMatchObject({
      full_name: 'Ali   Valiyev'.trim(),
      phone: '+998901234567', // maydonda probellar bor edi — serverga toza ketadi
      source: 'courses',
      website: '', // honeypot — odam uni to'ldirmaydi
    })
    expect(openLeadSuccess).toHaveBeenCalled()
  })

  it('yuborilgach maydonlar tozalanadi', async () => {
    const wrapper = mountForm()
    const name = inputByLabel(wrapper, forms.uz.fullName)
    const phone = inputByLabel(wrapper, forms.uz.phone)

    await name.setValue('Ali Valiyev')
    await phone.setValue('+998901234567')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(name.element.value).toBe('')
    expect(phone.element.value).toBe('+998 ')
  })

  it('telefon raqam yozilayotganda formatlanadi', async () => {
    const wrapper = mountForm()
    const phone = inputByLabel(wrapper, forms.uz.phone)

    await phone.setValue('998901234567')
    expect(phone.element.value).toBe('+998 90 123 45 67')
  })

  it("noto'g'ri yosh yuborishga to'sqinlik qiladi", async () => {
    const wrapper = mountForm({ withChildAge: true })

    await inputByLabel(wrapper, forms.uz.fullName).setValue('Ali Valiyev')
    await inputByLabel(wrapper, forms.uz.phone).setValue('+998901234567')
    await inputByLabel(wrapper, forms.uz.childAge).setValue('99')
    await wrapper.find('form').trigger('submit')

    expect(submitLead).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain(forms.uz.errorAge)
  })

  it("ajratilgan ism/familiya bitta `full_name` bo'lib ketadi", async () => {
    const wrapper = mountForm({ splitName: true })

    await inputByLabel(wrapper, forms.uz.firstName).setValue('Ali')
    await inputByLabel(wrapper, forms.uz.lastName).setValue('Valiyev')
    await inputByLabel(wrapper, forms.uz.phone).setValue('+998901234567')
    await wrapper.find('form').trigger('submit')

    expect(submitLead.mock.calls[0][0].full_name).toBe('Ali Valiyev')
  })

  it('serverdagi maydon xatosi shu maydon ostida chiqadi', async () => {
    submitLead.mockRejectedValue({
      detail: 'Некорректные данные.',
      errors: { phone: ['Этот номер уже занят.'] },
    })
    const wrapper = mountForm()

    await inputByLabel(wrapper, forms.uz.fullName).setValue('Ali Valiyev')
    await inputByLabel(wrapper, forms.uz.phone).setValue('+998901234567')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Этот номер уже занят.')
    expect(notify).toHaveBeenCalledWith('Некорректные данные.', 'error')
  })

  it('ikki marta bosilsa ham bitta ariza ketadi', async () => {
    let release
    submitLead.mockReturnValue(new Promise((resolve) => (release = resolve)))
    const wrapper = mountForm()

    await inputByLabel(wrapper, forms.uz.fullName).setValue('Ali Valiyev')
    await inputByLabel(wrapper, forms.uz.phone).setValue('+998901234567')

    await wrapper.find('form').trigger('submit')
    await wrapper.find('form').trigger('submit')
    release('ok')

    expect(submitLead).toHaveBeenCalledTimes(1)
  })
})
