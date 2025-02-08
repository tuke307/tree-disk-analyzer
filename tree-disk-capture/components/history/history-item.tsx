import { Pressable } from 'react-native';
import { Image } from 'expo-image';
import { router } from 'expo-router';
import { CaptureData } from '@/lib/constants/types';
import { CardWithImage, CardImage, CardHeader, CardDescription, CardTitle } from '@/components/ui/card';

interface Props {
  capture: CaptureData;
}

export function HistoryItem({ capture }: Props) {
  const formattedDate = new Date(capture.timestamp).toLocaleDateString('de-DE');
  
  return (
    <Pressable
      onPress={() => router.push(`/${capture.id}`)}
      className="mb-4"
    >
      {({ pressed }) => (
        <CardWithImage className={`${pressed ? 'opacity-70' : ''}`}>
          <CardImage>
            <Image
              source={{ uri: capture.uri }}
              className="w-20 h-20 rounded-lg"
              contentFit="cover"
            />
          </CardImage>
          <CardHeader className="flex-1 p-0">
            <CardTitle className="text-base">{capture.title}</CardTitle>
            <CardDescription>Captured: {formattedDate}</CardDescription>
          </CardHeader>
        </CardWithImage>
      )}
    </Pressable>
  );
}