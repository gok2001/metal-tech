
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,

    proxy: {
      // Ciência de Dados - Python
      "/api/stats/reservoirs": {
        target: "http://10.110.12.21:8000",
        changeOrigin: true,
        rewrite: (path) =>
          path.replace(
            /^\/api\/stats\/reservoirs/,
            "/api/v1/analytics/reservoirs"
          ),
      },

      // Backend principal - Java
      "/api": {
        target: "http://10.110.12.21:8080",
        changeOrigin: true,
      },
    },
  },
});
