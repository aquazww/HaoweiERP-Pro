import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        /* 将真实客户端 IP 标准化后通过 X-Forwarded-For 传给后端 */
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            let clientIp = req.socket.remoteAddress || req.connection.remoteAddress
            if (clientIp) {
              /* 剥离 IPv4-mapped IPv6 前缀，IPv4 客户端只显示纯 IPv4 */
              if (clientIp.startsWith('::ffff:')) {
                clientIp = clientIp.substring(7)
              }
              proxyReq.setHeader('X-Forwarded-For', clientIp)
            }
          })
        },
      }
    }
  }
})
