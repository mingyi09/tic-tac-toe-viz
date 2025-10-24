import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Set base for GitHub Pages deployment (replace with your repo name if different)
  base: '/tic-tac-toe-viz/',
})
