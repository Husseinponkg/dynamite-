import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/routing': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/packages': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/payments': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/vouchers': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/sessions': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/income': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/withdraws': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/captive': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
