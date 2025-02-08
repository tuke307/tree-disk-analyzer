import { useCameraPermissions } from 'expo-camera';
import { useCaptures } from '@/lib/hooks/use-captures';
import { analyzeImage } from '@/lib/constants/api';

export function useCamera() {
  const [permission, requestPermission] = useCameraPermissions();
  const { saveCapture } = useCaptures();

  const handleCapture = async (uri: string): Promise<string | undefined> => {
    try {
      const analysisResult = await analyzeImage(uri);
      const now = new Date();
      const id = now.toString();
      
      const newCapture = {
        id,
        title: 'analysis ' + now.toLocaleDateString('de-DE'),
        uri,
        timestamp: now.toISOString(),
        analysis: analysisResult,
      };
      
      await saveCapture(newCapture);

      return id;
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