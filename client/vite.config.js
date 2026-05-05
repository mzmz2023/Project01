// client/vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import http from 'node:http'; // <-- 引入http模块

export default defineConfig({
  plugins: [react()],
  server: {
    port: 8100, // 你的前端端口
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 后端地址
        changeOrigin: true, // 必须为true
        agent: new http.Agent({ family: 4 }), // <-- 关键项
      }
    }
  }
});