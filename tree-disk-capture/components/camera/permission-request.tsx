import { View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Label } from '@/components/ui/label';
import { Button } from '../ui/button';

interface PermissionRequestProps {
  onRequestPermission: () => void;
}

export function PermissionRequest({ onRequestPermission }: PermissionRequestProps) {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Label style={styles.title}>Camera Access Required</Label>
        <Label style={styles.description}>
          To analyze trees, we need permission to use your camera.
        </Label>

        <Button 
          style={styles.button}
          onPress={onRequestPermission}
        >
          <Label style={styles.buttonText}>Grant Access</Label>
        </Button>
      </View>
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