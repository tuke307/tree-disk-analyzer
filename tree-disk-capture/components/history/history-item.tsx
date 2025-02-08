import { Pressable, View } from 'react-native';
import { Image } from 'expo-image';
import { router } from 'expo-router';
import { CaptureData } from '@/lib/constants/types';
import { Button } from '../ui/button';
import { Text } from '../ui/text';

interface Props {
  capture: CaptureData;
}

export function HistoryItem({ capture }: Props) {
  const formattedDate = new Date(capture.timestamp).toLocaleDateString('de-DE');
  
  return (
    <Button
      variant="outline"
      onPress={() => router.push(`/${capture.id}`)}
      className="flex-1 w-full mb-4 p-0 overflow-hidden"
    >
      <View className="flex-row items-center w-full p-4 gap-4">
        <Image
          source={{ uri: capture.uri }}
          className="w-20 h-20 rounded-lg"
          contentFit="cover"
        />
        <View className="flex-1">
          <Text className="text-xl font-semibold leading-none tracking-tight">{capture.title}</Text>
          <Text className="text-sm text-muted-foreground">
            Captured: {formattedDate}
          </Text>
        </View>
      </View>
    </Button>
  );
}