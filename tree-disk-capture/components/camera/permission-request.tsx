import { View, Text, StyleSheet, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedView } from '../ThemedView';
import { ThemedText } from '../ThemedText';

interface PermissionRequestProps {
  onRequestPermission: () => void;
}

export function PermissionRequest({ onRequestPermission }: PermissionRequestProps) {
  return (
    <SafeAreaView style={styles.container}>
      <ThemedView style={styles.content}>
        <ThemedText style={styles.title}>Camera Access Required</ThemedText>
        <ThemedText style={styles.description}>
          To analyze trees, we need permission to use your camera.
        </ThemedText>
        <Pressable 
          style={styles.button}
          onPress={onRequestPermission}
        >
          <ThemedText style={styles.buttonText}>Grant Access</ThemedText>
        </Pressable>
      </ThemedView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 32,
    color: '#666',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});