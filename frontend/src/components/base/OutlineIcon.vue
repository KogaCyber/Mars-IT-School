<script setup>
/**
 * Nomi bo'yicha tanlanadigan chiziqli (outline) ikonka.
 * Backend `icon_name` maydonida shu nomlardan birini qaytaradi.
 */
defineProps({
  name: { type: String, required: true },
})

const PATHS = {
  brain:
    'M9 4.5a3 3 0 0 0-3 3 2.6 2.6 0 0 0-1.5 4.6A2.8 2.8 0 0 0 6 17.2a2.8 2.8 0 0 0 3 2.3V4.5ZM15 4.5a3 3 0 0 1 3 3 2.6 2.6 0 0 1 1.5 4.6A2.8 2.8 0 0 1 18 17.2a2.8 2.8 0 0 1-3 2.3V4.5ZM12 4.5v15',
  layers: 'M12 3.5 3.5 8 12 12.5 20.5 8 12 3.5ZM4 12.2 12 16.5l8-4.3M4 16.2 12 20.5l8-4.3',
  target:
    'M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17ZM12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8ZM12 11.2a.8.8 0 1 0 0 1.6.8.8 0 0 0 0-1.6Z',
  // Vizual dasturlash — Scratch bloklari
  blocks:
    'M4 4.5h6v6H4v-6ZM13.5 4.5h6.5v4.5h-6.5V4.5ZM4 13.5h4.5V20H4v-6.5ZM11.5 13.5h8.5V20h-8.5v-6.5Z',
  robot:
    'M8 8.5h8a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2ZM12 4.5v4M10 12.5h.01M14 12.5h.01M9.5 16h5M3.5 12v3M20.5 12v3',
  wrench:
    'M14.8 4.6a4.6 4.6 0 0 0-5.6 5.9L4 15.7v3.8h3.8l5.2-5.2a4.6 4.6 0 0 0 5.9-5.6l-2.8 2.8-2.4-.6-.6-2.4 2.7-2.9ZM6.6 17.4h.01',
  chip: 'M8 8h8v8H8V8ZM6 6h12v12H6V6ZM9.5 3.5v2.5M14.5 3.5v2.5M9.5 18v2.5M14.5 18v2.5M3.5 9.5H6M3.5 14.5H6M18 9.5h2.5M18 14.5h2.5',
  // Uchta blok — loyihaning modullari
  cubes: 'M4 4.5h6.5v6.5H4V4.5Z M13.5 4.5H20v6.5h-6.5V4.5Z M8.75 13h6.5v6.5h-6.5V13Z',
  chat: 'M4 5.5A1.5 1.5 0 0 1 5.5 4h13A1.5 1.5 0 0 1 20 5.5v9a1.5 1.5 0 0 1-1.5 1.5H9l-5 4v-4.2',
  spark: 'M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18',
  calendar:
    'M5 6.5A1.5 1.5 0 0 1 6.5 5h11A1.5 1.5 0 0 1 19 6.5v11a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 5 17.5v-11ZM8 3.5v3M16 3.5v3M5 9.5h14M9 13h.01M12 13h.01M15 13h.01M9 16h.01M12 16h.01',
  checklist:
    'M5.5 5.5A1.5 1.5 0 0 1 7 4h10a1.5 1.5 0 0 1 1.5 1.5v13A1.5 1.5 0 0 1 17 20H7a1.5 1.5 0 0 1-1.5-1.5v-13ZM8.5 9l1.5 1.5L13 7.5M8.5 15l1.5 1.5 3-3',
  clock: 'M12 3.5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17ZM12 7.5V12l3 1.8',
  // Kontaktlar bo'limi ikonkalari
  phone:
    'M7.6 3.8c.5 0 .9.3 1.1.8l1.2 3a1.2 1.2 0 0 1-.3 1.3l-1.3 1.2a12.5 12.5 0 0 0 5.6 5.6l1.2-1.3a1.2 1.2 0 0 1 1.3-.3l3 1.2c.5.2.8.6.8 1.1v2.5a2 2 0 0 1-2.2 2A16.8 16.8 0 0 1 3.6 6a2 2 0 0 1 2-2.2h2Z',
  mail: 'M4.5 6.5h15a1.5 1.5 0 0 1 1.5 1.5v8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 16V8a1.5 1.5 0 0 1 1.5-1.5ZM4 8.8l8 5 8-5',
  send: 'M20.5 3.5 3.5 10.2l6.6 2.6M20.5 3.5l-6.7 17-3.7-7.7M20.5 3.5 10.1 12.8',
  // Bitiruvchi shapkasi — o'qituvchi vakansiyasi
  cap: 'M12 4 2.5 8.5 12 13l9.5-4.5L12 4ZM6.5 10.8v4.4c0 1.6 2.5 2.8 5.5 2.8s5.5-1.2 5.5-2.8v-4.4M21 8.5v5.2',
  // Xodim nishoni (ID) — administrator
  badge:
    'M5.5 4h13A1.5 1.5 0 0 1 20 5.5v13a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18.5v-13A1.5 1.5 0 0 1 5.5 4ZM12 8.5a2 2 0 1 0 0 4 2 2 0 0 0 0-4ZM8 17c.6-1.6 2.1-2.5 4-2.5s3.4.9 4 2.5M9 4v2.5M15 4v2.5',
  // Naushnik — kol-markaz operatori
  headset:
    'M4.5 14v-2a7.5 7.5 0 0 1 15 0v2M4.5 13h1.7a1 1 0 0 1 1 1v3.5a1 1 0 0 1-1 1H5.7A1.2 1.2 0 0 1 4.5 17.3V13ZM19.5 13h-1.7a1 1 0 0 0-1 1v3.5a1 1 0 0 0 1 1h.5a1.2 1.2 0 0 0 1.2-1.2V13ZM17.5 18.5v.5a2 2 0 0 1-2 2H13',
  users:
    'M15.5 19.5v-1.7a3.5 3.5 0 0 0-3.5-3.5H7a3.5 3.5 0 0 0-3.5 3.5v1.7M9.5 10.8a3.4 3.4 0 1 0 0-6.8 3.4 3.4 0 0 0 0 6.8ZM20.5 19.5v-1.7a3.5 3.5 0 0 0-2.6-3.4M15.4 4.2a3.4 3.4 0 0 1 0 6.6',
}
</script>

<template>
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      :d="PATHS[name] || PATHS.brain"
      stroke="currentColor"
      stroke-width="1.3"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>
