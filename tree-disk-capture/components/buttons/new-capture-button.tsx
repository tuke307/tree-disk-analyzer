import { Pressable, Text, View, Dimensions } from 'react-native';
import { ThemedView } from '../ThemedView';
import { ThemedText } from '../ThemedText';

interface Props {
  onPress: () => void;
}

export function NewCaptureButton({ onPress }: Props) {
  const screenHeight = Dimensions.get('window').height;
  const buttonHeight = screenHeight / 3;

  return (
    <Pressable 
      onPress={onPress}
      style={{ height: buttonHeight }}
      className="w-full p-4"
    >
      {({ pressed }) => (
        <ThemedView 
          className={`flex-1 rounded-2xl items-center justify-center
            ${pressed ? 'opacity-70' : 'opacity-100'}`}
          style={{
            borderWidth: 1,
            borderColor: '#374151', // Equivalent to gray-700
          }}
        >
          <ThemedText className="font-semibold text-4xl">
            New Capture
          </ThemedText>
          <ThemedText className="mt-4">
            Tap to analyze a tree disk
          </ThemedText>
        </ThemedView>
      )}
    </Pressable>
  );
}