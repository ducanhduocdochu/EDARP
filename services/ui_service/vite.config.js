import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api/auth": {
        target: "http://localhost:5001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/auth/, "/auth"),
      },
      "/api/users": {
        target: "http://localhost:5001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/users/, "/users"),
      },
      "/api/projects": {
        target: "http://localhost:5002",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/projects/, "/projects"),
      },
      "/api/documents": {
        target: "http://localhost:5002",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/documents/, "/documents"),
      },
      "/api/index": {
        target: "http://localhost:5004",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/index/, "/index"),
      },
      "/api/query": {
        target: "http://localhost:5005",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/query/, "/query"),
      },
    },
  },
});
