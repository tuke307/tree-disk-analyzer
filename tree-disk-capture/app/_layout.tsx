import "@/global.css";
import { Stack } from "expo-router";
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from "react";
import { Platform } from "react-native";
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NAV_THEME } from "@/lib/constants/theme";
import { Theme, ThemeProvider, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { LoadSkiaWeb } from "@shopify/react-native-skia/lib/module/web";
import { PortalHost } from '@rn-primitives/portal';
import { SQLiteProvider } from 'expo-sqlite';
import { EXPO_PUBLIC_DB_FILE_NAME } from "@/lib/constants/database";
import { ThemeContextProvider, useThemeContext } from "@/lib/hooks/use-theme-context";

const LIGHT_THEME: Theme = {
  ...DefaultTheme,
  dark: false,
  colors: {
    ...DefaultTheme.colors,
    ...NAV_THEME.light,
  },
};
const DARK_THEME: Theme = {
  ...DarkTheme,
  dark: true,
  colors: {
    ...DarkTheme.colors,
    ...NAV_THEME.dark,
  },
};

export {
  // Catch any errors thrown by the Layout component.
  ErrorBoundary,
} from 'expo-router';

// Prevent the splash screen from auto-hiding before getting the color scheme.
if (Platform.OS !== 'web') {
  // Silently handle splash screen errors in Expo Go
  (async () => {
    try {
      await SplashScreen.preventAutoHideAsync();
    } catch (error) {
      // Ignore - splash screen not available in Expo Go
    }
  })();
}

function RootLayoutContent() {
  const { colorScheme, isLoaded } = useThemeContext();

  useEffect(() => {
    if (Platform.OS === 'web') {
      // Adds the background color to the html element to prevent white background on overscroll.
      document.documentElement.classList.add('bg-background');
      // Load Skia on web
      LoadSkiaWeb({ locateFile: () => "/canvaskit.wasm" })
        .catch((error) => console.error("Failed to load Skia on web:", error));
    }
  }, []);

  useEffect(() => {
    if (isLoaded && Platform.OS !== 'web') {
      SplashScreen.hideAsync().catch(() => {
        // Ignore errors in Expo Go where splash screen might not be registered
      });
    }
  }, [isLoaded]);

  if (!isLoaded) {
    return null;
  }

  const isDarkColorScheme = colorScheme === 'dark';

  return (
    <ThemeProvider value={isDarkColorScheme ? DARK_THEME : LIGHT_THEME}>
      <SafeAreaProvider>
        <Stack
          screenOptions={{
            headerShown: false,
          }} />
        <PortalHost />
      </SafeAreaProvider>
    </ThemeProvider>
  );
}

export default function RootLayout() {
  return (
    <ThemeContextProvider>
      <SQLiteProvider
        databaseName={EXPO_PUBLIC_DB_FILE_NAME}
        options={{ enableChangeListener: true }}>
        <RootLayoutContent />
      </SQLiteProvider>
    </ThemeContextProvider>
  );
}
