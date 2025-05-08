// craco.config.js
module.exports = {
    devServer: (devServerConfig) => {
      // 显式允许所有主机访问，避免 allowedHosts 报错
      devServerConfig.allowedHosts = 'all';
      return devServerConfig;
    },
  };
  