import React, { createContext, useContext, useEffect, useState } from 'react';
import { Platform, Appearance } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

type ColorScheme = 'light' | 'dark';

interface ThemeContextType {
  colorScheme: ColorScheme;
  setColorScheme: (scheme: ColorScheme) => void;
  toggleColorScheme: () => void;
  isLoaded: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeContextProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
  const [colorScheme, setColorSchemeState] = useState<ColorScheme>('light');
  const [isLoaded, setIsLoaded] = useState(false);

  // Apply color scheme to web
  const applyColorScheme = (scheme: ColorScheme) => {
    // For Web - add/remove dark class to document root
    if (Platform.OS === 'web' && typeof document !== 'undefined') {
      const root = document.documentElement;
      if (scheme === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    }
  };

  useEffect(() => {
    (async () => {
      const theme = await AsyncStorage.getItem('theme');
      if (!theme) {
        await AsyncStorage.setItem('theme', 'light');
        setColorSchemeState('light');
        applyColorScheme('light');
        setIsLoaded(true);
        return;
      }
      const colorTheme = theme === 'dark' ? 'dark' : 'light';
      setColorSchemeState(colorTheme);
      applyColorScheme(colorTheme);
      setIsLoaded(true);
    })();
  }, []);

  const setColorScheme = async (scheme: ColorScheme) => {
    setColorSchemeState(scheme);
    applyColorScheme(scheme);
    await AsyncStorage.setItem('theme', scheme);
  };

  const toggleColorScheme = async () => {
    const newScheme = colorScheme === 'dark' ? 'light' : 'dark';
    setColorSchemeState(newScheme);
    applyColorScheme(newScheme);
    await AsyncStorage.setItem('theme', newScheme);
  };

  return (
    <ThemeContext.Provider value={{ colorScheme, setColorScheme, toggleColorScheme, isLoaded }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useThemeContext() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useThemeContext must be used within a ThemeContextProvider');
  }
  return context;
}
