import { View } from 'react-native';
import { Image } from 'expo-image';
import { router } from 'expo-router';
import { Capture } from '@/lib/database/models';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';

interface Props {
  capture: Capture;
}

export function HistoryItem({ capture }: Props) {
  const formattedDate = new Date(Number(capture.timestamp)).toLocaleDateString('de-DE');

  return (
    <Button
      variant="outline"
      onPress={() => router.push(`/${capture.id}`)}
      className="flex-1 w-full mb-4 p-0 overflow-hidden"
      style={{ minHeight: 80 }}
    >
      <View className="flex-row items-center w-full p-4 gap-4">
        <Image
          source={{ uri: capture.image_base64 }}
          className="w-20 h-20 rounded-lg"
          contentFit="cover"
        />
        <View className="flex-1">
          <Text className="text-xl leading-none tracking-tight">{capture.title}</Text>
          <Text className="text-sm text-muted-foreground">
            Captured: {formattedDate}
          </Text>
        </View>
      </View>
    </Button>
  );
}