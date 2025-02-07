import { View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

interface PermissionRequestProps {
  onRequestPermission: () => void;
}

export function PermissionRequest({ onRequestPermission }: PermissionRequestProps) {
  return (
    <SafeAreaView className="flex-1">
      <View className="flex-1 justify-center items-center px-5">
        <Label className="text-2xl font-bold mb-4">Camera Access Required</Label>
        <Label className="text-base text-center mb-8 ">
          To analyze trees, we need permission to use your camera.
        </Label>

        <Button onPress={onRequestPermission} className="px-8 py-4 rounded-lg">
          <Label className="text-base font-semibold">Grant Access</Label>
        </Button>
      </View>
    </SafeAreaView>
  );
}
