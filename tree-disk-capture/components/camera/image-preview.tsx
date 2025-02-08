import { StyleSheet, SafeAreaView, View } from 'react-native';
import { Image } from 'expo-image';
import { Button } from '@/components/ui/button';
import { RotateCcwIcon } from '@/lib/icons/RotateCcwIcon';
import { SaveIcon } from '@/lib/icons/SaveIcon';
import { Text } from '@/components/ui/text';

interface ImagePreviewProps {
  uri: string;
  onRetake: () => void;
  onSave: () => void;
  isLoading?: boolean;
}

export function ImagePreview({
  uri,
  onRetake,
  onSave,
  isLoading = false
}: ImagePreviewProps) {
  return (
    <SafeAreaView className="flex-1">
      <View className="flex-1">
        <Image
          source={{ uri }}
          style={styles.preview}
          contentFit="contain"
        />

        <View className='flex-row justify-between p-8'>
          <Button
            onPress={onRetake}
            className='flex-row gap-2 items-center'>
            <RotateCcwIcon className='text-primary-foreground'/>
            <Text>
              Retake
            </Text>
          </Button>

          <Button
            onPress={onSave}
            disabled={isLoading}
            className='flex-row gap-2 items-center'
          >
            {isLoading ? (
              <Text>
                Analyzing...
              </Text>
            ) : (
              <View className='flex-row gap-2 items-center'>
                <SaveIcon className='text-primary-foreground'/>
                <Text>
                  Save
                </Text>
              </View>
            )}
          </Button>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  preview: {
    flex: 1,
    margin: 32,
  },
});