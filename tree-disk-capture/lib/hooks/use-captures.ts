import { useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { CaptureData } from '@/lib/constants/types';

export function useCaptures() {
  const [captures, setCaptures] = useState<CaptureData[]>([]);

  useEffect(() => {
    loadCaptures();
  }, []);

  const loadCaptures = async () => {
    try {
      const storedCaptures = await AsyncStorage.getItem('captures');
      if (storedCaptures) {
        setCaptures(JSON.parse(storedCaptures));
      }
    } catch (error) {
      console.error('Error loading captures:', error);
    }
  };

  const saveCapture = async (capture: CaptureData) => {
    try {
      const updatedCaptures = [capture, ...captures];
      await AsyncStorage.setItem('captures', JSON.stringify(updatedCaptures));
      setCaptures(updatedCaptures);
    } catch (error) {
      console.error('Error saving capture:', error);
    }
  };

  const getCaptureById = (id: string) => {
    return captures.find(capture => capture.id === id);
  };

  return { captures, saveCapture, getCaptureById };
}