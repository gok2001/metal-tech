import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import basicSsl from "@vitejs/plugin-basic-ssl";

export default defineConfig(function (config) {
  var env = loadEnv(config.mode, process.cwd(), "");

  return {
    plugins: [react(), basicSsl()],
    server: {
      host: true,
      port: 5174,
      strictPort: true,
      proxy: {
        "/api": {
          target: env.API_PROXY || "http://10.110.12.57:8080",
          changeOrigin: true,
        },
      },
    },
  };
});