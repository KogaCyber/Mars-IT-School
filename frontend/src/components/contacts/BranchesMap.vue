<script setup>
/**
 * Filiallar xaritasi — Leaflet, to'q (dark) plitkalar va Mars sayyorasi
 * ko'rinishidagi nishonlar. Nishon bosilganda `select` hodisasi chiqadi.
 *
 * Xarita sichqoncha g'ildiragi bilan zumlanmaydi: sahifa scroll'i buzilmasin.
 */
import 'leaflet/dist/leaflet.css'

import L from 'leaflet'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import marsMarker from '@/assets/images/mars-planet.webp'

const props = defineProps({
  /** Koordinatasi bor filiallar. */
  branches: { type: Array, required: true },
  /** Ajratib ko'rsatiladigan filial slug'i. */
  activeSlug: { type: String, default: '' },
})

const emit = defineEmits(['select'])

/** Toshkent markazi — koordinatalar bo'lmasa shu ko'rsatiladi. */
const TASHKENT = [41.3111, 69.2797]

const container = ref(null)
let map = null
let markers = new Map()

/** Mars nishoni: tanlanganda kattaroq va nur bilan. */
function icon(isActive) {
  const size = isActive ? 62 : 48
  return L.divIcon({
    className: 'mars-marker',
    html: `<img loading="lazy" decoding="async" src="${marsMarker}" alt="" class="${isActive ? 'is-active' : ''}" />`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

function draw() {
  if (!map) return

  markers.forEach((marker) => marker.remove())
  markers = new Map()

  const points = []
  props.branches.forEach((branch) => {
    const latLng = [branch.latitude, branch.longitude]
    const marker = L.marker(latLng, {
      icon: icon(branch.slug === props.activeSlug),
      title: branch.name,
      keyboard: true,
      alt: branch.name,
    })
      .addTo(map)
      .on('click', () => emit('select', branch))

    markers.set(branch.slug, marker)
    points.push(latLng)
  })

  if (points.length > 1) {
    map.fitBounds(L.latLngBounds(points), { padding: [70, 70], maxZoom: 13 })
  } else if (points.length === 1) {
    map.setView(points[0], 13)
  }
}

onMounted(() => {
  map = L.map(container.value, {
    center: TASHKENT,
    zoom: 11,
    zoomControl: false,
    scrollWheelZoom: false,
    attributionControl: false,
  })

  // Esri «Dark Gray Canvas» — kalitsiz ishlaydigan to'q xarita: asos + yozuvlar
  const ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas'
  L.tileLayer(`${ESRI}/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}`, {
    maxZoom: 16,
  }).addTo(map)
  L.tileLayer(`${ESRI}/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}`, {
    maxZoom: 16,
    pane: 'shadowPane',
  }).addTo(map)

  draw()
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})

watch(() => props.branches, draw, { deep: true })

// Faqat nishonlar ko'rinishi yangilanadi — xarita joyidan qimirlamaydi.
watch(
  () => props.activeSlug,
  (slug) => {
    markers.forEach((marker, key) => marker.setIcon(icon(key === slug)))
  },
)
</script>

<template>
  <div ref="container" class="branches-map h-full w-full" />
</template>

<style>
/* Leaflet konteyneri — sayt foni va shrifti bilan uyg'un.

   MUHIM: Leaflet o'z qatlamlariga `z-index: 400…700` beradi. Konteyner o'zi
   alohida "stacking context" yaratmasa, bu qatlamlar modal oynalardan
   (filial paneli — z-65, lightbox — z-70) ustun chiqib, ularning ustiga
   chizilardi. `isolation` va `z-index: 0` xaritani o'z ichida ushlab turadi. */
.branches-map {
  position: relative;
  z-index: 0;
  isolation: isolate;
  background: #0d0d0d;
  font-family: inherit;
}

/* Esri plitkalari maketdagidek qoraytiriladi (yozuvlar alohida qatlamda — ular yorqin qoladi) */
.branches-map .leaflet-tile-pane {
  filter: brightness(0.45) saturate(0.85) contrast(1.05);
}

.mars-marker img {
  width: 100%;
  height: 100%;
  cursor: pointer;
  filter: drop-shadow(0 0.5rem 1.25rem rgba(0, 0, 0, 0.65));
  transition:
    transform 0.25s ease,
    filter 0.25s ease;
}

.mars-marker img:hover {
  transform: scale(1.12);
}

/* Tanlangan filial — atrofida to'q sariq nur */
.mars-marker img.is-active {
  filter: drop-shadow(0 0 1.1rem rgba(233, 73, 33, 0.95))
    drop-shadow(0 0 2.2rem rgba(233, 73, 33, 0.55));
}
</style>
