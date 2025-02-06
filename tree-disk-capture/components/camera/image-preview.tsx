import { View, Text, Pressable } from 'react-native';
import { Image } from 'expo-image';
import { Feather } from '@expo/vector-icons';
import { ThemedView } from '../ThemedView';
import { ThemedText } from '../ThemedText';

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
    <ThemedView className="flex-1">
      {/* Image Preview */}
      <Image
        source={{ uri }}
        className="flex-1"
        contentFit="contain"
      />

      {/* Controls Overlay */}
      <ThemedView className="absolute bottom-0 left-0 right-0 p-6">
        <ThemedView className="flex-row justify-between items-center">
          {/* Retake Button */}
          <Pressable
            onPress={onRetake}
            className="flex-row items-center px-4 py-2 rounded-full"
          >
            {({ pressed }) => (
              <>
                <Feather 
                  name="rotate-ccw" 
                  size={20} 
                  color="white"
                  style={{ opacity: pressed ? 0.7 : 1, marginRight: 8 }}
                />
                <ThemedText className="font-medium">
                  Retake
                </ThemedText>
              </>
            )}
          </Pressable>

          {/* Save Button */}
          <Pressable
            onPress={onSave}
            disabled={isLoading}
            className="flex-row items-center px-6 py-3 rounded-full disabled:opacity-50"
          >
            {({ pressed }) => (
              <>
                {isLoading ? (
                  <ThemedView className="flex-row items-center">
                    <ThemedText className="font-medium">
                      Analyzing...
                    </ThemedText>
                  </ThemedView>
                ) : (
                  <ThemedView 
                    className="flex-row items-center"
                    style={{ opacity: pressed ? 0.7 : 1 }}
                  >
                    <Feather 
                      name="check" 
                      size={20} 
                      color="white" 
                      style={{ marginRight: 8 }}
                    />
                    <ThemedText className="font-medium">
                      Save
                    </ThemedText>
                  </ThemedView>
                )}
              </>
            )}
          </Pressable>
        </ThemedView>
      </ThemedView>
    </ThemedView>
  );
}