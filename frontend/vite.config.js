import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // 讓 Docker 外部可以連線
    port: 5173,      // Vite 預設 Port
    watch: {
      usePolling: true // Windows Docker 有時候需要這個才能熱更新
    },
    allowedHosts: ['.ngrok-free.app']
  }
})