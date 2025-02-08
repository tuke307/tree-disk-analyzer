import { SafeAreaView, View } from 'react-native';
import { Image } from 'expo-image';
import { Button } from '@/components/ui/button';
import { RotateCcwIcon } from '@/lib/icons/RotateCcwIcon';
import { ArrowRightIcon } from '@/lib/icons/ArrowRightIcon';
import { Text } from '@/components/ui/text';

interface ImagePreviewProps {
  uri: string;
  onRetake: () => void;
  onSave: () => void;
}

export function ImagePreview({
  uri,
  onRetake,
  onSave,
}: ImagePreviewProps) {
  return (
    <SafeAreaView className="flex-1">
      <View className="flex-1">
        <Image
          source={{ uri }}
          className='flex-1 m-32'
          contentFit="contain"
        />

        <View className='flex-row justify-between p-8'>
          <Button
            onPress={onRetake}
            className='flex-row gap-2 items-center'>
            <RotateCcwIcon className='text-primary-foreground' />
            <Text>
              Retake
            </Text>
          </Button>

          <Button
            onPress={onSave}

            className='flex-row gap-2 items-center'
          >
            <ArrowRightIcon className='text-primary-foreground' />
            <Text>
              Next
            </Text>
          </Button>
        </View>
      </View>
    </SafeAreaView>
  );
}
