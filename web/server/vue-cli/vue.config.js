const path = require("path");

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src")
      }
    }
  },

  devServer: {
    port: 8080,
    proxy: {
      "/v6.62": {
        target: "http://localhost:8001",
        changeOrigin: true,
        secure: false
      },
    }
  }
};
