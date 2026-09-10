import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'

/**
 * Kod uslubi (bo'shliqlar, qator uzunligi) Prettier zimmasida —
 * ESLint faqat xatoliklarni tekshiradi.
 */
export default [
  { ignores: ['dist/**', 'node_modules/**'] },
  js.configs.recommended,
  ...pluginVue.configs['flat/essential'],
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        console: 'readonly',
        Intl: 'readonly',
        IntersectionObserver: 'readonly',
        MutationObserver: 'readonly',
        requestAnimationFrame: 'readonly',
        cancelAnimationFrame: 'readonly',
        URLSearchParams: 'readonly',
        matchMedia: 'readonly',
        FormData: 'readonly',
        File: 'readonly',
      },
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  },
  {
    // Konfiguratsiya va build skriptlari Node muhitida ishlaydi.
    files: ['vite.config.js', 'eslint.config.js', 'scripts/**/*.mjs', 'tests/**/*.js'],
    languageOptions: {
      globals: {
        process: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        AbortSignal: 'readonly',
      },
    },
  },
]
