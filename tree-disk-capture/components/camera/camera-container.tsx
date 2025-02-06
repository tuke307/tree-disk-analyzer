import { CameraView } from "expo-camera";
import { useRef, useState } from "react";
import { StyleSheet } from "react-native";
import { CameraControls } from './camera-controls';
import { ImagePreview } from './image-preview';
import { ThemedText } from "../ThemedText";
import { ThemedView } from "../ThemedView";

interface Props {
  onCapture: (uri: string) => Promise<void>;
  onCaptureSaved: () => void;
}

export function CameraContainer({ onCapture, onCaptureSaved }: Props) {
  // @ts-ignore: just being lazy with types here
  const cameraRef = useRef<CameraView>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uri, setUri] = useState<string | null>(null);

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
    <ThemedView style={styles.container}>
      <ThemedView style={{ flex: 1 }}>
      <ThemedText type="subtitle">Camera</ThemedText>
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
          <ThemedView className="flex-1">
            <CameraView
              className="flex-1 w-full h-full"
              ref={cameraRef}
              mode="picture"
              facing="back"
            >
              <CameraControls
                onCapture={handleTakePhoto}
                showFlip={false}
              />
            </CameraView>
          </ThemedView>
        )}
      </ThemedView>
    </ThemedView>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center'
  },
  camera: {
    flex: 1,
  },
  buttonContainer: {
    flex: 1,
    flexDirection: "row",
    backgroundColor: "transparent",
    margin: 64,
  },
  button: {
    flex: 1,
    alignSelf: "flex-end",
    alignItems: "center",
  },
  text: {
    fontSize: 24,
    fontWeight: "bold",
    color: "white",
  },
});