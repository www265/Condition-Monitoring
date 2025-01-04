const path = require('path');
const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  publicPath: process.env.NODE_ENV === 'production' ? '/' : './',
  outputDir: 'dist',
  assetsDir: 'assets',
  lintOnSave: false,
  devServer: {
    headers: {
      'X-Content-Type-Options': 'nosniff'
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // 替换为你的后端服务地址
        changeOrigin: true,
        pathRewrite: { '^/api': '' }
      }
    },
    historyApiFallback: true
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  }
});