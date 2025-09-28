module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        vue: "@vue/compat"
      }
    }
  },
  transpileDependencies: ["vuetify"],
};
