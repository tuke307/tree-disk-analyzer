import { View } from 'react-native';
import { router } from 'expo-router';
import { CameraContainer } from '@/components/camera/camera-container';
import { useCamera } from '@/lib/hooks/use-camera';
import { PermissionRequest } from '@/components/camera/permission-request';

export default function Capture() {
  const { permission, requestPermission, handleCapture } = useCamera();

  if (!permission?.granted) {
    return <PermissionRequest onRequestPermission={requestPermission} />;
  }

  if (!permission) {
    // Camera permissions are still loading.
    return <View />;
  }

  return (
    <CameraContainer 
      onCapture={handleCapture}
      onCaptureSaved={(id) => router.replace(`/${id}`)}
      onClose={() => router.replace('/')}
    />
  );
}