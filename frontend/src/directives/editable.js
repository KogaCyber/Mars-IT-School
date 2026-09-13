/**
 * `v-editable="['home.hero', 'title']"` — element muharrirda tahrirlanadigan
 * bo'lim maydoniga bog'lanadi.
 *
 * Direktiva faqat `data-*` atributlarini qo'yadi. Bosishni bitta global
 * tinglovchi ushlaydi (`installEditableClicks`), ajratib ko'rsatishni esa
 * `body.is-editing [data-edit-key]` CSS qoidasi beradi. Shu tufayli oddiy
 * tashrifchi uchun bu direktiva hech narsa qilmaydi va hech narsani
 * sekinlashtirmaydi.
 */
import { useEditorStore } from '@/stores/editor'

function apply(el, binding) {
  const [key, field] = Array.isArray(binding.value) ? binding.value : [binding.value, null]
  if (!key) return
  el.dataset.editKey = key
  if (field) el.dataset.editField = field
  else delete el.dataset.editField
}

export const editable = {
  mounted: apply,
  updated: apply,
}

/** Bir marta, ilova ishga tushganda. */
export function installEditableClicks() {
  if (typeof document === 'undefined') return
  document.addEventListener(
    'click',
    (event) => {
      const editor = useEditorStore()
      if (!editor.editing || !editor.isEditor) return
      const target = event.target.closest?.('[data-edit-key]')
      if (!target) return
      // Muharrir panelining o'zi ichidagi bosishlar — oddiy.
      if (target.closest('[data-editor-ui]')) return
      event.preventDefault()
      event.stopPropagation()
      editor.open(target.dataset.editKey, target.dataset.editField || null)
    },
    true,
  )
}
