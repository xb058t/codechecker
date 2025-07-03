module.exports = {
  lintOnSave: false,
  devServer: {
    proxy: "http://localhost:8001"
  },
  chainWebpack: config => {
    config.module.rules.delete("eslint");
  }
};
