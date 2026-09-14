/**
 * `live.notify()` — xodim saqlagach barcha yuklovchilarni darhol yangilaydi
 * (5 soniyalik versiya so'rovini kutmasdan). Busiz qo'shilgan yangilik/vakansiya
 * sahifada faqat qo'lda F5 bosilgach ko'rinardi.
 */
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useLiveStore } from '@/stores/live'

describe('live.notify', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('barcha obunachilarni chaqiradi', () => {
    const live = useLiveStore()
    const a = vi.fn()
    const b = vi.fn()
    live.subscribe(a)
    live.subscribe(b)

    live.notify()

    expect(a).toHaveBeenCalledTimes(1)
    expect(b).toHaveBeenCalledTimes(1)
  })

  it('obunani bekor qilgach chaqirmaydi', () => {
    const live = useLiveStore()
    const a = vi.fn()
    const off = live.subscribe(a)

    off()
    live.notify()

    expect(a).not.toHaveBeenCalled()
  })
})
