import { Pressable } from 'react-native';
import { FontAwesome6 } from '@expo/vector-icons';
import { Ionicons } from '@expo/vector-icons';
import { ThemedView } from '../ThemedView';

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
    <>
      {/* Top Controls */}
      <ThemedView className="absolute top-12 left-0 right-0 flex-row justify-between px-6">
        <Pressable
          onPress={onClose}
          className="w-12 h-12 items-center justify-center"
        >
          {({ pressed }) => (
            <Ionicons
              name="close"
              size={32}
              style={{ opacity: pressed ? 0.7 : 1 }}
            />
          )}
        </Pressable>

        <Pressable
          onPress={onFlashToggle}
          className="w-12 h-12 items-center justify-center"
        >
          {({ pressed }) => (
            <Ionicons
              name={flashEnabled ? "flash" : "flash-off"}
              size={32}
              style={{ opacity: pressed ? 0.7 : 1 }}
            />
          )}
        </Pressable>
      </ThemedView>

      {/* Bottom Capture Button */}
      <ThemedView className="absolute bottom-12 left-0 right-0 items-center">
        <Pressable
          onPress={onCapture}
          className="w-20 h-20 rounded-full border-4 items-center justify-center"
        >
          {({ pressed }) => (
            <FontAwesome6
              name="camera"
              size={32}
              style={{ opacity: pressed ? 0.7 : 1 }}
            />
          )}
        </Pressable>
      </ThemedView>
    </>
  );
}