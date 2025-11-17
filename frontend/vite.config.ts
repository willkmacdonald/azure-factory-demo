import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5174, // Using port 5174 to avoid conflicts with other projects
    strictPort: false, // If 5174 is taken, Vite will try the next available port
  },
})
