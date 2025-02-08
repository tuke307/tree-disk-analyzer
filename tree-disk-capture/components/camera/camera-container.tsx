import { CameraView } from "expo-camera";
import { useRef, useState } from "react";
import { StyleSheet, View } from "react-native";
import * as ImagePicker from 'expo-image-picker';
import { CameraControls } from '@/components/camera/camera-controls';
import { ImagePreview } from '@/components/camera/image-preview';


interface Props {
  onCapture: (uri: string) => Promise<string | undefined>;
  onCaptureSaved: (id: string) => void;
  onClose: () => void;
}

export function CameraContainer({ onCapture, onCaptureSaved, onClose }: Props) {
  const cameraRef = useRef<CameraView>(null);
  const [uri, setUri] = useState<string | null>(null);
  const [flashEnabled, setFlashEnabled] = useState(false);

  const handleTakePhoto = async () => {
    try {
      const photo = await cameraRef.current?.takePictureAsync();

      console.log(JSON.stringify(photo));

      if (photo?.uri) {
        setUri(photo.uri);
      }
    } catch (error) {
      console.error('Failed to take photo:', error);
    }
  };

  const handleGalleryPress = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    
    if (permission.status !== 'granted') {
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 1,
    });

    console.log(result);

    if (!result.canceled && result.assets[0]) {
      setUri(result.assets[0].uri);
    }
  };

  const handleSave = async () => {
    if (uri) {
      const captureId = await onCapture(uri);
      if (captureId) {
        onCaptureSaved(captureId);
      }
    }
  };

  return (
    <View className="flex-1">
      {uri ? (
        <ImagePreview
          uri={uri}
          onRetake={() => setUri(null)}
          onSave={async () => {
            await handleSave();
          }}
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
            onGalleryPress={handleGalleryPress}
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