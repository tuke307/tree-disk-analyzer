import { View, Image } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { useCaptures } from '@/lib/hooks/use-captures';
import { Text } from '@/components/ui/text';

export default function CaptureDetails() {
  const { id } = useLocalSearchParams();
  const { getCaptureById } = useCaptures();
  const capture = getCaptureById(id as string);

  if (!capture) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <Text className="text-xl">Capture not found</Text>
      </View>
    );
  }

  return (
    <View className="flex-1 p-4">
      <Image
        source={{ uri: capture.uri }}
        className="w-full h-64 rounded-lg mb-4"
        resizeMode="cover"
      />
      <Text className="text-lg mb-2">
        Predicted Age: {capture.analysis.predictedAge}
      </Text>
      <Text className="text-lg mb-2">
        Location: {capture.analysis.predictedLocation}
      </Text>
      <Text className="text-lg">
        Captured: {new Date(capture.timestamp).toLocaleDateString()}
      </Text>
    </View>
  );
}