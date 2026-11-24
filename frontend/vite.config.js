import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      // In dev, /documents, /query and /health go to the FastAPI backend.
      "/documents": "http://localhost:8000",
      "/query": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
  preview: { port: 3000, host: true },
});
