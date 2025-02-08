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

  const updateCaptureTitle = async (id: string, title: string) => {
    const updatedCaptures = captures.map(capture =>
      capture.id === id ? { ...capture, title } : capture
    );
    try {
      await AsyncStorage.setItem('captures', JSON.stringify(updatedCaptures));
      setCaptures(updatedCaptures);
    } catch (error) {
      console.error('Error updating capture title:', error);
    }
  };

  const deleteCapture = async (id: string) => {
    const updatedCaptures = captures.filter(capture => capture.id !== id);
    try {
      await AsyncStorage.setItem('captures', JSON.stringify(updatedCaptures));
      setCaptures(updatedCaptures);
    } catch (error) {
      console.error('Error deleting capture:', error);
    }
  };

  const refreshCaptures = async () => {
    await loadCaptures();
  };

  const updateCapture = async (updatedCapture: CaptureData) => {
    const updatedCaptures = captures.map(c => 
      c.id === updatedCapture.id ? updatedCapture : c
    );
    try {
      await AsyncStorage.setItem('captures', JSON.stringify(updatedCaptures));
      setCaptures(updatedCaptures);
    } catch (error) {
      console.error('Error updating capture:', error);
    }
  };

  return { captures, saveCapture, getCaptureById, updateCaptureTitle, deleteCapture, refreshCaptures, updateCapture };
}