import { useCameraPermissions } from 'expo-camera';
import { useCaptures } from '@/lib/hooks/use-captures';
import * as Crypto from 'expo-crypto';

export function useCamera() {
  const [permission, requestPermission] = useCameraPermissions();
  const { addCapture } = useCaptures();

  const handleCapture = async (imageBase64: string, width: number, height: number): Promise<string | undefined> => {
    try {
      const newCapture = {
        id: Crypto.randomUUID(),
        title: "analysis " + Date.now().toLocaleString('de-DE'),
        image_base64: imageBase64,
        timestamp: new Date(),
        width: width,
        height: height
      };

      await addCapture(newCapture);

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