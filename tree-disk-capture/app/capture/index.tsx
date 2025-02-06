import { View } from 'react-native';
import { router } from 'expo-router';
import { CameraContainer } from '@/components/camera/camera-container';
import { useCamera } from '@/hooks/use-camera';
import { PermissionRequest } from '@/components/camera/permission-request';
import { ThemedView } from '@/components/ThemedView';

export default function Capture() {
  const { permission, requestPermission, handleCapture } = useCamera();

  if (!permission?.granted) {
    return <PermissionRequest onRequestPermission={requestPermission} />;
  }

  if (!permission) {
    // Camera permissions are still loading.
    return <ThemedView />;
  }

  return (
    <CameraContainer 
      onCapture={handleCapture}
      onCaptureSaved={() => router.replace('/')}
      onClose={() => router.replace('/')}
    />
  );
}