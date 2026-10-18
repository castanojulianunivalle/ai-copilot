import { readFileSync } from 'node:fs';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// HU-10: la versión sale de package.json y el commit del entorno de build
// (Render pone RENDER_GIT_COMMIT; GitHub Actions, GITHUB_SHA). Quedan dentro
// del bundle para que la pantalla muestre qué versión está corriendo.
const { version } = JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf-8'));
const commit = (process.env.RENDER_GIT_COMMIT || process.env.GITHUB_SHA || 'local').slice(0, 7);

export default defineConfig({
  plugins: [react()],
  define: {
    __APP_VERSION__: JSON.stringify(version),
    __APP_COMMIT__: JSON.stringify(commit),
  },
});
