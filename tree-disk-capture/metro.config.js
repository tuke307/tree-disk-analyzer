const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname, {
    isCSSEnabled: true,
});

config.resolver.assetExts.push('wasm');
config.transformer.getTransformOptions = async () => ({
    transform: {
        experimentalImportSupport: false,
        inlineRequires: true,
    },
});

config.resolver.sourceExts.push('sql');

module.exports = withNativeWind(config, { input: "./global.css" });