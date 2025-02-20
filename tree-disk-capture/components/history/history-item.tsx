import { View } from 'react-native';
import { Image } from 'expo-image';
import { router } from 'expo-router';
import { CaptureWithAnalysis } from '@/lib/database/models';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';

interface Props {
  capture: CaptureWithAnalysis;
}

export function HistoryItem({ capture }: Props) {
  const captureCreatedAt = new Date(capture.createdAt).toLocaleDateString('de-DE');

  return (
    <Button
      variant="outline"
      onPress={() => router.push(`/${capture.id}`)}
      className="w-full p-0"
      style={{ height: 100 }}
    >
      <View className="flex-row items-center w-full p-2 gap-4">
        <View className="w-20 h-20 rounded-lg bg-muted-foreground overflow-hidden">
          <Image
            source={{ uri: capture.imageBase64 }}
            transition={1000}
            // somehow tailwind is ignored here, so we need to use the style prop
            style={{ width: '100%', height: '100%' }}
            contentFit="cover"
          />
        </View>

        <View className="flex-1">
          <Text className="text-xl leading-none tracking-tight">{capture.title}</Text>
          <Text className="text-sm text-muted-foreground">
            Captured: {captureCreatedAt}
          </Text>
        </View>
      </View>
    </Button>
  );
}