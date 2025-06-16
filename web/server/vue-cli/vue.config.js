module.exports = {
  devServer: {
    proxy: {
      '^/v6.61': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '^/123': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '^/1231': {
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
};
