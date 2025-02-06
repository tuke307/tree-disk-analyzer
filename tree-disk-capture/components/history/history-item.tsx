import { View } from 'react-native';
import { Image } from 'expo-image';
import { router } from 'expo-router';
import { CaptureData } from '@/lib/constants/types';
import { Label } from '@/components/ui/label';
import { Button } from '../ui/button';
import { Text } from '../ui/text';

interface Props {
  capture: CaptureData;
}

export function HistoryItem({ capture }: Props) {
  const formattedDate = new Date(capture.timestamp).toLocaleDateString();
  
  return (
    <Button
      onPress={() => router.push(`/${capture.id}`)}
      className="rounded-lg p-4 mb-4 flex-row"
    >
      <Image
        source={{ uri: capture.uri }}
        className="w-20 h-20 rounded-lg"
        contentFit="cover"
      />
      <View className="ml-4 flex-1">
        <Text className="font-semibold mb-1">
          Tree Age: {capture.analysis.predictedAge}
        </Text>
        <Text>
          Location: {capture.analysis.predictedLocation}
        </Text>
        <Text>
          Captured: {formattedDate}
        </Text>
      </View>
    </Button>
  );
}