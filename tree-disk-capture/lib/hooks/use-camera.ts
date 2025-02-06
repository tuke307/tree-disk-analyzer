import { useCameraPermissions } from 'expo-camera';
import { useCaptures } from './use-captures';
import { analyzeImage } from '@/lib/constants/api';

export function useCamera() {
  const [permission, requestPermission] = useCameraPermissions();
  const { saveCapture } = useCaptures();

  const handleCapture = async (uri: string) => {
    try {
      const analysisResult = await analyzeImage(uri);
      
      const newCapture = {
        id: Date.now().toString(),
        uri,
        timestamp: new Date().toISOString(),
        analysis: analysisResult,
      };
      
      await saveCapture(newCapture);
    } catch (error) {
      console.error('Error processing capture:', error);
    }
  };

  return {
    permission,
    requestPermission,
    handleCapture,
  };
}