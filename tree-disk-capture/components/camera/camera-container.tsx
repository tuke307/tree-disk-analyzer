import { CameraView } from "expo-camera";
import { useRef, useState } from "react";
import { StyleSheet, View } from "react-native";
import * as ImagePicker from 'expo-image-picker';
import { CameraControls } from '@/components/camera/camera-controls';
import { ImagePreview } from '@/components/camera/image-preview';


interface Props {
  onCapture: (uri: string, width: number, height: number) => Promise<string | undefined>;
  onCaptureSaved: (id: string) => void;
  onClose: () => void;
}

export function CameraContainer({ onCapture, onCaptureSaved, onClose }: Props) {
  const cameraRef = useRef<CameraView>(null);
  const [flashEnabled, setFlashEnabled] = useState(false);
  const [photoData, setPhotoData] = useState<{ base64: string, width: number, height: number } | null>(null);

  const handleTakePhoto = async () => {
    try {
      const photo = await cameraRef.current?.takePictureAsync({
        quality: 1,
        base64: true,
      });

      if (photo) {
        console.log('Photo taken:', photo);

        if (photo.base64) {
          setPhotoData({
            base64: photo.base64,
            width: photo.width,
            height: photo.height,
          });
        } else {
          console.error("Photo base64 is undefined.");
        }
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
      base64: true,
    });

    console.log("ImagePicker result:", result);

    if (!result.canceled && result.assets[0]) {
      const asset = result.assets[0];

      if (asset.base64) {
        setPhotoData({
          base64: asset.base64,
          width: asset.width,
          height: asset.height,
        });
      } else {
        console.error("Asset base64 is undefined.");
      }
    }
  };

  const handleSave = async () => {
    console.log('Saving capture:', photoData);
    if (photoData) {
      const captureId = await onCapture(photoData.base64, photoData.width, photoData.height);
      if (captureId) {
        onCaptureSaved(captureId);
      }
    }
  };

  return (
    <View className="flex-1">
      {photoData ? (
        <ImagePreview
          base64={photoData?.base64 || ''}
          onRetake={() => setPhotoData(null)}
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