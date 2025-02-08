import { useState, useEffect, useCallback } from 'react';  // Add useCallback
import { View, Image, ScrollView } from 'react-native';
import { useLocalSearchParams, useNavigation, useRouter } from 'expo-router';
import { useCaptures } from '@/lib/hooks/use-captures';
import { Text } from '@/components/ui/text';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { analyzeImage } from '@/lib/constants/api';  // Add this import

export default function CaptureDetails() {
  const { id } = useLocalSearchParams();
  const navigation = useNavigation();
  const router = useRouter();
  const { getCaptureById, updateCaptureTitle, deleteCapture, updateCapture } = useCaptures();  // Add updateCapture
  const capture = getCaptureById(id as string);

  const [title, setTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(true);

  // Add debounced save
  const debouncedUpdateTitle = useCallback(
    async (newTitle: string) => {
      if (capture?.id) {
        await updateCaptureTitle(capture.id, newTitle);
      }
    },
    [capture?.id, updateCaptureTitle]
  );

  // Handle title changes
  const handleTitleChange = (newTitle: string) => {
    setTitle(newTitle);
    debouncedUpdateTitle(newTitle);
  };

  useEffect(() => {
    if (capture) {
      const formattedDate = new Date(capture.timestamp).toLocaleDateString('de-DE');
      setTitle(capture.title || `analysis ${formattedDate}`);
      setIsAnalyzing(!capture.analysis);
    }
  }, [capture]);

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

  const handleRetryAnalysis = async () => {
    if (!capture) return;

    setIsAnalyzing(true);
    try {
      const newAnalysis = await analyzeImage(capture.uri);
      await updateCapture({
        ...capture,
        analysis: newAnalysis
      });
    } catch (error) {
      console.error('Failed to reanalyze:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <ScrollView className="flex-1">
      <View className="flex-1 p-4">
        <View className="flex-1 gap-2">
          <Image
            source={{ uri: capture.uri }}
            className="w-full rounded-lg mb-4"
            style={{ aspectRatio: 1 }}
            resizeMode="contain"
          />

          <Input
            value={title}
            onChangeText={handleTitleChange}
            className="mb-4 pl-4"
            style={{ width: 250 }}
          />

          {isAnalyzing ? (
            <View className="items-center py-4">
              <Text>Analyzing image...</Text>
            </View>
          ) : (
            <View className="flex-1">
              <View className="mb-12">
                <Text className="text-lg">
                  Predicted Age: {capture.analysis.predictedAge}
                </Text>
                <Text className="text-lg">
                  Captured: {formattedDate}
                </Text>
              </View>

              <View className="flex-row justify-start gap-4 mb-4">
                <Button
                  variant="outline"
                  onPress={handleRetryAnalysis}
                >
                  <Text>Retry Analysis</Text>
                </Button>

                <Dialog>
                  <DialogTrigger asChild>
                    <Button className="flex-initial" variant='destructive'>
                      <Text>Delete</Text>
                    </Button>
                  </DialogTrigger>
                  <DialogContent className='sm:max-w-[425px]'>
                    <DialogHeader>
                      <DialogTitle>Delete Capture</DialogTitle>
                      <DialogDescription>
                        Are you sure you want to delete this capture? This action cannot be undone.
                      </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                      <DialogClose asChild>
                        <Button>
                          <Text>Cancel</Text>
                        </Button>
                      </DialogClose>
                      <Button
                        variant='destructive'
                        onPress={async () => {
                          await deleteCapture(capture.id);
                          router.replace('/');
                        }}>
                        <Text>Delete</Text>
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </View>
            </View>
          )}
        </View>
      </View>
    </ScrollView>
  );
}