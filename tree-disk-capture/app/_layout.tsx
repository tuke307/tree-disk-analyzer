import "@/global.css";
import { SplashScreen, Stack } from "expo-router";
import { useEffect, useState } from "react";
import { View, StyleSheet, StatusBar, Platform } from "react-native";
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NAV_THEME } from "@/lib/constants/theme";
import { Theme, ThemeProvider, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { useColorScheme } from "@/lib/hooks/use-color-scheme";
import AsyncStorage from "@react-native-async-storage/async-storage";

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

  useEffect(() => {
    (async () => {
      const theme = await AsyncStorage.getItem('theme');
      if (Platform.OS === 'web') {
        // Adds the background color to the html element to prevent white background on overscroll.
        document.documentElement.classList.add('bg-background');
      }
      if (!theme) {
        AsyncStorage.setItem('theme', colorScheme);
        setIsColorSchemeLoaded(true);
        return;
      }
      const colorTheme = theme === 'dark' ? 'dark' : 'light';
      if (colorTheme !== colorScheme) {
        setColorScheme(colorTheme);

        setIsColorSchemeLoaded(true);
        return;
      }
      setIsColorSchemeLoaded(true);
    })().finally(() => {
      SplashScreen.hideAsync();
    });
  }, []);

  if (!isColorSchemeLoaded) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <ThemeProvider value={isDarkColorScheme ? DARK_THEME : LIGHT_THEME}>
        <View style={StyleSheet.absoluteFill}>
          <StatusBar />
          <Stack
            screenOptions={{
              headerShown: false,
              presentation: 'fullScreenModal'
            }}
          >
            <Stack.Screen
              name="index"
              options={{
                title: 'Tree Rings',
              }}
            />
            <Stack.Screen
              name="capture"
              options={{
                title: 'New Capture',
                presentation: 'fullScreenModal',
              }}
            />
          </Stack>
        </View>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
