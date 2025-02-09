import "@/global.css";
import { SplashScreen, Stack } from "expo-router";
import { useEffect, useState } from "react";
import { Platform } from "react-native";
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NAV_THEME } from "@/lib/constants/theme";
import { Theme, ThemeProvider, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { useColorScheme } from "@/lib/hooks/use-color-scheme";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { LoadSkiaWeb } from "@shopify/react-native-skia/lib/module/web";

const LIGHT_THEME: Theme = {
  ...DefaultTheme,
  colors: NAV_THEME.light,
};
const DARK_THEME: Theme = {
  ...DarkTheme,
  colors: NAV_THEME.dark,
};

export {
  // Catch any errors thrown by the Layout component.
  ErrorBoundary,
} from 'expo-router';

// Prevent the splash screen from auto-hiding before getting the color scheme.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const { colorScheme, setColorScheme, isDarkColorScheme } = useColorScheme();
  const [isColorSchemeLoaded, setIsColorSchemeLoaded] = useState(false);
  const [skiaLoaded, setSkiaLoaded] = useState(false);
  const [isMounted, setIsMounted] = useState(true);

  // Load theme from AsyncStorage.
  useEffect(() => {
    loadTheme();
    return () => setIsMounted(false);
  }, []);

  // Load Skia assets.
  useEffect(() => {
    if (Platform.OS === "web") {
      console.debug("Loading Skia on web...");
      LoadSkiaWeb({ locateFile: () => "/canvaskit.wasm" })
        .then(() => setSkiaLoaded(true))
        .catch((error) => {
          console.error("Failed to load Skia on web:", error);
          setSkiaLoaded(true);
        });
    } else {
      setSkiaLoaded(true);
    }
  }, []);

  // Hide the splash screen once both color scheme & Skia are loaded.
  useEffect(() => {
    if (isColorSchemeLoaded) {
      hideSplashScreen();
    }
  }, [isColorSchemeLoaded]);

  const hideSplashScreen = async () => {
    try {
      await SplashScreen.hideAsync();
    } catch (error) {
      console.error('Failed to hide splash screen:', error);
    }
  };

  const loadTheme = async () => {
    try {
      const theme = await AsyncStorage.getItem('theme');

      if (Platform.OS === 'web') {
        document.documentElement.classList.add('bg-background');
      }

      if (!theme) {
        await AsyncStorage.setItem('theme', colorScheme);
      } else {
        const colorTheme = theme === 'dark' ? 'dark' : 'light';
        if (colorTheme !== colorScheme) {
          setColorScheme(colorTheme);
        }
      }

      if (isMounted) {
        setIsColorSchemeLoaded(true);
      }
    } catch (error) {
      console.error('Failed to load theme:', error);
      // Set loaded state even on error to prevent hanging
      setIsColorSchemeLoaded(true);
    }
  };

  // render nothing until both theme and Skia are loaded.
  if (!isColorSchemeLoaded || !skiaLoaded) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <ThemeProvider value={isDarkColorScheme ? DARK_THEME : LIGHT_THEME}>
        <Stack
          screenOptions={{
            headerShown: false,
            presentation: 'fullScreenModal'
          }} />
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
