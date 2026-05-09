import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/import': 'http://127.0.0.1:8000',
      '/courses': 'http://127.0.0.1:8000',
      '/search': 'http://127.0.0.1:8000',
      '/questions': 'http://127.0.0.1:8000',
      '/qa': 'http://127.0.0.1:8000',
      '/documents': 'http://127.0.0.1:8000',
      '/conversations': 'http://127.0.0.1:8000',
      '/openapi.json': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: fileURLToPath(new URL('../app/web/static', import.meta.url)),
    emptyOutDir: false,
  },
})
