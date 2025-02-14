import { View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { XIcon } from '@/lib/icons/XIcon';

interface PermissionRequestProps {
  onRequestPermission: () => void;
  onClose: () => void;
}

export function PermissionRequest({ onRequestPermission, onClose }: PermissionRequestProps) {
  return (
    <SafeAreaView className="flex-1">
      {/* Top Controls */}
      <View className="absolute top-12 left-0 right-0 flex-row justify-between p-4">
        <Button
          onPress={onClose}
          variant="ghost"
          size="icon"
        >
          <XIcon className='text-foreground' />
        </Button>
      </View>

      <View className="flex-1 justify-center items-center px-5">
        <Text className="text-2xl font-bold mb-4">Camera Access Required</Text>
        <Text className="text-base text-center mb-8 ">
          To analyze trees, we need permission to use your camera.
        </Text>

        <Button onPress={onRequestPermission} className="px-8 py-4 rounded-lg">
          <Text>Grant Access</Text>
        </Button>
      </View>
    </SafeAreaView>
  );
}
