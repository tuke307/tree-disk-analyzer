import { View } from 'react-native';
import { FlashlightIcon } from '@/lib/icons/FlashlightIcon';
import { FlashlightOffIcon } from '@/lib/icons/FlashlightOffIcon';
import { XIcon } from '@/lib/icons/XIcon';
import { CameraIcon } from '@/lib/icons/CameraIcon';
import { ImagesIcon } from '@/lib/icons/ImagesIcon';
import { Button } from '@/components/ui/button';

interface CameraControlsProps {
  onCapture: () => void;
  onClose: () => void;
  onGalleryPress: () => void;
  onFlashToggle: () => void;
  flashEnabled: boolean;
}

export function CameraControls({
  onCapture,
  onClose,
  onGalleryPress,
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
          <XIcon className='text-foreground' />
        </Button>

        <Button
          onPress={onFlashToggle}
          variant="ghost"
          size="icon"
        >
          {flashEnabled ? (
            <FlashlightIcon className='text-foreground' />
          ) : (
            <FlashlightOffIcon className='text-foreground' />
          )}
        </Button>
      </View>

      {/* Bottom Capture Button */}
      <View className="absolute bottom-12 left-0 right-0 flex-row justify-between items-center px-12">
        <Button
          onPress={onGalleryPress}
          variant="ghost"
          size="icon"
        >
          <ImagesIcon className='text-foreground' />
        </Button>

        <Button
          onPress={onCapture}
          variant="ghost"
          size="icon"
          className='h-12 w-12'
        >
          <CameraIcon size={32} className='text-foreground' />
        </Button>

        <View /> {/* Placeholder for symmetry */}
      </View>
    </View>
  );
}