import { View, Pressable } from 'react-native';
import { FontAwesome6 } from '@expo/vector-icons';
import { Feather } from '@expo/vector-icons';
import { ThemedView } from '../ThemedView';

interface CameraControlsProps {
  onCapture: () => void;
  onFlipCamera?: () => void;
  showFlip?: boolean;
}

export function CameraControls({ 
  onCapture, 
  onFlipCamera, 
  showFlip = true 
}: CameraControlsProps) {
  return (
    <ThemedView className="absolute bottom-10 left-0 right-0">
      <ThemedView className="flex-row items-center justify-between px-8">
        {/* Spacer or additional control on the left */}
        <ThemedView className="w-12 h-12" />

        {/* Capture Button */}
        <Pressable
          onPress={onCapture}
          className="w-20 h-20 rounded-full border-4 items-center justify-center"
        >
          {({ pressed }) => (
            <ThemedView 
              className={`w-16 h-16 rounded-full ${
                pressed ? 'opacity-70' : 'opacity-100'
              }`}
            />
          )}
        </Pressable>

        {/* Flip Camera Button */}
        {showFlip && (
          <Pressable 
            onPress={onFlipCamera}
            className="w-12 h-12 items-center justify-center"
          >
            {({ pressed }) => (
              <FontAwesome6 
                name="camera-rotate" 
                size={28} 
                color="white" 
                style={{ opacity: pressed ? 0.7 : 1 }}
              />
            )}
          </Pressable>
        )}
        
        {/* If no flip button, add spacer */}
        {!showFlip && <ThemedView className="w-12 h-12" />}
      </ThemedView>
    </ThemedView>
  );
}