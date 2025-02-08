import { useState, useEffect } from 'react';
import { View, Image } from 'react-native';
import { useLocalSearchParams, useNavigation, useRouter } from 'expo-router';
import { useCaptures } from '@/lib/hooks/use-captures';
import { Text } from '@/components/ui/text';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function CaptureDetails() {
  const { id } = useLocalSearchParams();
  const navigation = useNavigation();
  const router = useRouter();
  const { getCaptureById, updateCaptureTitle, deleteCapture } = useCaptures();
  const capture = getCaptureById(id as string);

  const [title, setTitle] = useState('');
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    if (capture) {
      const formattedDate = new Date(capture.timestamp).toLocaleDateString('de-DE');
      setTitle(capture.title || `analysis ${formattedDate}`);
    }
  }, [capture]);

  useEffect(() => {
    setIsSaved(false);
  }, [title]);

  // Set modal header title to current title
  useEffect(() => {
    navigation.setOptions({ title });
  }, [title, navigation]);

  if (!capture) {
    return (
      <View className="flex-1 items-center justify-center p-4">
        <Text className="text-xl">Capture not found</Text>
      </View>
    );
  }

  const formattedDate = new Date(capture.timestamp).toLocaleDateString('de-DE');

  return (
    <View className="flex-1 p-4">
      <View className="flex-1 gap-2">
        <Image
          source={{ uri: capture.uri }}
          className="w-full h-64 rounded-lg mb-4"
          resizeMode="cover"
        />

        <Input
          value={title}
          onChangeText={setTitle}
        />

        <Text className="text-lg">
          Predicted Age: {capture.analysis.predictedAge}
        </Text>
        <Text className="text-lg">
          Location: {capture.analysis.predictedLocation}
        </Text>
        <Text className="text-lg">
          Captured: {formattedDate}
        </Text>
      </View>

      <View className="gap-2 mt-auto">
        <Button
          onPress={async () => {
            await updateCaptureTitle(capture.id, title);
            setIsSaved(true);
          }}>
          <Text>{isSaved ? 'Saved!' : 'Save'}</Text>
        </Button>
        <Button
          variant='destructive'
          onPress={async () => {
            await deleteCapture(capture.id);
            router.replace('/');
          }}>
          <Text>Delete</Text>
        </Button>
      </View>
    </View>
  );
}