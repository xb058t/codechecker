module.exports = {
  devServer: {
    proxy: {
      '^/v6': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '^/Configuration': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '^/ServerInfo': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '^/CodeCheckerService': {
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    }
  }
}
