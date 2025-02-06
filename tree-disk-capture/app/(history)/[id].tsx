import { View, Text, Image } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { useCaptures } from '@/hooks/use-captures';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';

export default function CaptureDetails() {
  const { id } = useLocalSearchParams();
  const { getCaptureById } = useCaptures();
  const capture = getCaptureById(id as string);

  if (!capture) {
    return (
      <ThemedView className="flex-1 items-center justify-center p-4">
        <ThemedText className="text-xl">Capture not found</ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView className="flex-1 p-4">
      <Image
        source={{ uri: capture.uri }}
        className="w-full h-64 rounded-lg mb-4"
        resizeMode="cover"
      />
      <ThemedText className="text-lg mb-2">
        Predicted Age: {capture.analysis.predictedAge}
      </ThemedText>
      <ThemedText className="text-lg mb-2">
        Location: {capture.analysis.predictedLocation}
      </ThemedText>
      <ThemedText className="text-lg">
        Captured: {new Date(capture.timestamp).toLocaleDateString()}
      </ThemedText>
    </ThemedView>
  );
}