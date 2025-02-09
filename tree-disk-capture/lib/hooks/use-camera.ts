import { useCameraPermissions } from 'expo-camera';
import { useCaptures } from '@/lib/hooks/use-captures';

export function useCamera() {
  const [permission, requestPermission] = useCameraPermissions();
  const { addCapture } = useCaptures();

  const handleCapture = async (uri: string, width: number, height: number): Promise<string | undefined> => {
    try {
      return await addCapture(uri, width, height);
    } catch (error) {
      console.error('Error processing capture:', error);
      return undefined;
    }
  };

  return {
    permission,
    requestPermission,
    handleCapture,
  };
}