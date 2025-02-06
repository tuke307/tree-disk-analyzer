import { ThemedView } from "@/components/ThemedView";
import "../global.css";
import FontAwesome from "@expo/vector-icons/FontAwesome";
import { useFonts } from "expo-font";
import { SplashScreen, Stack } from "expo-router";
import { memo, useEffect } from "react";
import { View, StyleSheet, StatusBar } from "react-native";

export {
  // Catch any errors thrown by the Layout component.
  ErrorBoundary,
} from "expo-router";

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require("../assets/fonts/SpaceMono-Regular.ttf"),
    ...FontAwesome.font,
  });

  // Expo Router uses Error Boundaries to catch errors in the navigation tree.
  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return <RootLayoutNav />;
}

function RootLayoutNav() {
  return (
    <ThemedView style={StyleSheet.absoluteFill}>
      <StatusBar/>
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
    </ThemedView>
  );
}