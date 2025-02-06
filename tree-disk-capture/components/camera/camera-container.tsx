import { CameraView } from "expo-camera";
import { useRef, useState } from "react";
import { StyleSheet, View } from "react-native";
import { CameraControls } from './camera-controls';
import { ImagePreview } from './image-preview';

interface Props {
  onCapture: (uri: string) => Promise<void>;
  onCaptureSaved: () => void;
  onClose: () => void;
}

export function CameraContainer({ onCapture, onCaptureSaved, onClose }: Props) {
  const cameraRef = useRef<CameraView>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uri, setUri] = useState<string | null>(null);
  const [flashEnabled, setFlashEnabled] = useState(false);

  const handleTakePhoto = async () => {
    try {
      const photo = await cameraRef.current?.takePictureAsync();

      alert(`photo captured with dimensions: ${photo!.width} x ${photo!.height}`);
      console.log(JSON.stringify(photo));

      if (photo?.uri) {
        setUri(photo.uri);
      }
    } catch (error) {
      console.error('Failed to take photo:', error);
    }
  };

  const handleSave = async () => {
    if (uri) {
      await onCapture(uri);
      onCaptureSaved();
    }
  };

  return (
    <View className="flex-1">
      {uri ? (
        <ImagePreview
          uri={uri}
          onRetake={() => setUri(null)}
          onSave={async () => {
            setIsAnalyzing(true);
            await handleSave();
            setIsAnalyzing(false);
          }}
          isLoading={isAnalyzing}
        />
      ) : (
        <CameraView
          style={styles.camera}
          ref={cameraRef}
          mode="picture"
          facing="back"
          flash={flashEnabled ? "on" : "off"}
        >
          <CameraControls
            onCapture={handleTakePhoto}
            onClose={onClose}
            onFlashToggle={() => setFlashEnabled(!flashEnabled)}
            flashEnabled={flashEnabled}
          />
        </CameraView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  camera: {
    flex: 1,
  },
});