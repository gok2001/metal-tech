
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ command }) => ({
  plugins: [react()],

  base: command === "build" ? "/metal-tech/" : "/",

  server: {
    port: 5174,
    strictPort: true,

    proxy: {
      "/api": {
        target: "http://10.110.12.57:8080",
        changeOrigin: true,
      },
    },
  },
}));
