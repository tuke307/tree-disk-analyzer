import { useCameraPermissions } from 'expo-camera';
import { useCaptures } from '@/lib/hooks/use-captures';

export function useCamera() {
  const [permission, requestPermission] = useCameraPermissions();
  const { addCapture } = useCaptures();

  const handleCapture = async (imageBase64: string, width: number, height: number): Promise<string | undefined> => {
    try {
      const newCapture = await addCapture({
        imageBase64,
        width,
        height,
      });

      if (!newCapture) {
        throw new Error('Error adding capture');
      }

      return newCapture.id;
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