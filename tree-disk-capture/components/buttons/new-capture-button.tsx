import { View } from 'react-native';
import { Button } from '../ui/button';
import { Text } from '../ui/text';

interface Props {
  onPress: () => void;
}

export function NewCaptureButton({ onPress }: Props) {
  return (
    <Button
      onPress={onPress}
      variant="outline"
      className="flex-1 w-full h-full p-4"
    >
      <View className="w-full flex flex-col flex-1 items-center justify-center">
        <Text className="font-bold">New Capture</Text>
        <Text className="">Tap to analyze a tree disk</Text>
      </View>
    </Button>
  );
}