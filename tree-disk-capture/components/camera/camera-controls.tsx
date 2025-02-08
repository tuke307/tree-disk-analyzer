import { View } from 'react-native';
import { FlashlightIcon } from '@/lib/icons/FlashlightIcon';
import { FlashlightOffIcon } from '@/lib/icons/FlashlightOffIcon';
import { XIcon } from '@/lib/icons/XIcon';
import { CameraIcon } from '@/lib/icons/CameraIcon';
import { Button } from '@/components/ui/button';

interface CameraControlsProps {
  onCapture: () => void;
  onClose: () => void;
  onFlashToggle: () => void;
  flashEnabled: boolean;
}

export function CameraControls({
  onCapture,
  onClose,
  onFlashToggle,
  flashEnabled
}: CameraControlsProps) {

  return (
    <View className="flex-1">
      {/* Top Controls */}
      <View className="absolute top-12 left-0 right-0 flex-row justify-between p-4">
        <Button
          onPress={onClose}
          variant="ghost"
          size="icon"
        >
          <XIcon />
        </Button>

        <Button
          onPress={onFlashToggle}
          variant="ghost"
          size="icon"
        >

          {flashEnabled ? (
            <FlashlightIcon />
          ) : (
            <FlashlightOffIcon />
          )}

        </Button>
      </View>

      {/* Bottom Capture Button */}
      <View className="absolute bottom-12 left-0 right-0 flex-row justify-center p-4">
        <Button
          onPress={onCapture}
          variant="ghost"
          size="icon"
          className='h-12 w-12'
        >
          <CameraIcon size={32} />
        </Button>
      </View>
    </View>
  );
}