import path from "path";
import tailwindcss from "@tailwindcss/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

const apiProxy = {
  "/api": {
    target: "http://127.0.0.1:8000",
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api/, ""),
  },
} as const;

export default defineConfig({
  server: {
    host: "::",
    port: 8080,
    proxy: apiProxy,
  },
  preview: {
    port: 8080,
    proxy: apiProxy,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  plugins: [
    tailwindcss(),
    tanstackStart({ srcDirectory: "src" }),
    // O plugin do React deve vir depois do TanStack Start
    react(),
    tsconfigPaths(),
  ],
});