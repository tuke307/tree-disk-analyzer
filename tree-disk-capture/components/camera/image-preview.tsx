import { View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Image } from 'expo-image';
import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { ArrowRightIcon, RotateCcwIcon } from 'lucide-react-native';

interface ImagePreviewProps {
  base64: string;
  onRetake: () => void;
  onSave: () => void;
}

export function ImagePreview({
  base64,
  onRetake,
  onSave,
}: ImagePreviewProps) {
  return (
    <SafeAreaView className="flex-1">
      <View className="flex-1 m-12">
        <Image
          source={{ uri: base64 }}
          contentFit="contain"
          transition={1000}
          // somehow tailwind is ignored here, so we need to use the style prop
          style={{ flex: 1, width: '100%', height: '100%' }}
        />
      </View>

      <View className='flex-row justify-between p-8'>
        <Button
          onPress={onRetake}
          className='flex-row gap-2 items-center'>
          <Icon as={RotateCcwIcon} className='text-primary-foreground' />
          <Text>
            Retake
          </Text>
        </Button>

        <Button
          onPress={onSave}
          className='flex-row gap-2 items-center'
        >
          <Icon as={ArrowRightIcon} className='text-primary-foreground' />
          <Text>
            Next
          </Text>
        </Button>

      </View>
    </SafeAreaView>
  );
}
