import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://127.0.0.1:8000'

  return {
    plugins: [vue(), tailwindcss()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      port: 5173,
      strictPort: true,
      // Lokalda backendga proxy — CORS bilan ovora bo'lmaslik uchun.
      proxy: {
        '/api': { target: proxyTarget, changeOrigin: true },
        '/media': { target: proxyTarget, changeOrigin: true },
      },
    },
    // Testlar `@` aliasini va shu konfiguratsiyani ishlatadi (vitest).
    test: {
      environment: 'node',
      include: ['tests/**/*.test.js'],
    },
    build: {
      target: 'es2022',
      sourcemap: false,
      chunkSizeWarningLimit: 700,
      rollupOptions: {
        output: {
          // Kutubxonalar alohida chunk'ga chiqadi — sahifalar tez yangilanadi.
          //
          // Leaflet (xarita, ~150 KB) faqat «Kontaktlar» sahifasida kerak.
          // Ilgari u ham umumiy `vendor` ichida edi va HAR BIR sahifada,
          // jumladan bosh sahifada yuklanardi. Endi u alohida chunk — xarita
          // komponenti ochilgandagina yuklab olinadi.
          manualChunks(id) {
            if (!id.includes('node_modules')) return null
            if (id.includes('leaflet')) return 'leaflet'
            return 'vendor'
          },
        },
      },
    },
  }
})
