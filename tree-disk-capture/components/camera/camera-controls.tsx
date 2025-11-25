import { View } from 'react-native';
import { Icon } from '@/components/ui/icon';
import { Button } from '@/components/ui/button';
import { CameraIcon, InfoIcon, FlashlightIcon, FlashlightOffIcon, ImagesIcon } from 'lucide-react-native';

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
          <Icon as={InfoIcon} className='text-foreground' />
        </Button>

        <Button
          onPress={onFlashToggle}
          variant="ghost"
          size="icon"
        >
          {flashEnabled ? (
            <Icon as={FlashlightIcon} className='text-foreground' />
          ) : (
            <Icon as={FlashlightOffIcon} className='text-foreground' />
          )}
        </Button>
      </View>

      {/* Bottom Capture Button */}
      <View className="absolute bottom-12 left-0 right-0 flex-row items-center px-12">
        <View className="flex-1">
          <Button
            onPress={onGalleryPress}
            variant="ghost"
            size="icon"
          >
            <Icon as={ImagesIcon} className='text-foreground' />
          </Button>
        </View>

        <View className="flex-1 items-center">
          <Button
            onPress={onCapture}
            variant="ghost"
            size="icon"
            className='h-12 w-12'
          >
            <Icon as={CameraIcon} size={32} className='text-foreground' />
          </Button>
        </View>

        <View className="flex-1" />
      </View>
    </View>
  );
}