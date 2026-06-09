import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// FastAPI serves the production build from backend/static; in dev, Vite proxies
// /api to the uvicorn process on :8000.
export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
