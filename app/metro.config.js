const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

const originalResolveRequest = config.resolver.resolveRequest;
config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (moduleName === 'react-native-svg' && platform === 'web') {
    return context.resolveRequest(context, 'react-native-svg/src/ReactNativeSVG.web', platform);
  }
  if (originalResolveRequest) {
    return originalResolveRequest(context, moduleName, platform);
  }
  return context.resolveRequest(context, moduleName, platform);
};

module.exports = config;
