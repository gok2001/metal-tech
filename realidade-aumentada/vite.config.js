
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import basicSsl from "@vitejs/plugin-basic-ssl";

export default defineConfig(({ command }) => ({
  plugins: [
    react(),
    basicSsl(),
  ],

  base: command === "build" ? "/metal-tech/" : "/",

  server: {
    host: "192.168.0.14",
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
