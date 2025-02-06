import { View, Text, Pressable } from 'react-native';
import { Image } from 'expo-image';
import { router } from 'expo-router';
import { CaptureData } from '@/constants/types';
import { ThemedView } from '../ThemedView';
import { ThemedText } from '../ThemedText';

interface Props {
  capture: CaptureData;
}

export function HistoryItem({ capture }: Props) {
  const formattedDate = new Date(capture.timestamp).toLocaleDateString();
  
  return (
    <Pressable 
      onPress={() => router.push(`/${capture.id}`)}
      className="bg-gray-800 rounded-lg p-4 mb-4 flex-row"
    >
      <Image
        source={{ uri: capture.uri }}
        className="w-20 h-20 rounded-lg"
        contentFit="cover"
      />
      <ThemedView className="ml-4 flex-1">
        <ThemedText className="font-semibold mb-1">
          Tree Age: {capture.analysis.predictedAge}
        </ThemedText>
        <ThemedText>
          Location: {capture.analysis.predictedLocation}
        </ThemedText>
        <ThemedText>
          Captured: {formattedDate}
        </ThemedText>
      </ThemedView>
    </Pressable>
  );
}