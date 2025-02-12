import { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, Dimensions } from 'react-native';
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
import { detectPith, detectRings, segmentImage } from '@/lib/api/api';
import { ImageOverlay } from '@/components/history/image-overlay';
import { Capture, Pith, Rings, Segmentation } from '@/lib/database/models';
import { ProgressStep } from '@/components/history/progress-step';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function CaptureDetails() {
  // Updated to include the optional query parameter "analyze"
  const { id, analyze } = useLocalSearchParams();
  const navigation = useNavigation();
  const router = useRouter();
  const { getCaptureById, deleteCapture, updateCapture } = useCaptures();

  const [capture, setCapture] = useState<Capture | null>(null);
  const [title, setTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Calculate display dimensions based on screen width
  const screenWidth = Dimensions.get('window').width * 0.9; // 90% of screen width for padding
  const originalWidth = capture?.width || 800;
  const originalHeight = capture?.height || 600;
  const aspectRatio = originalWidth / originalHeight;
  const displayWidth = Math.min(originalWidth, screenWidth);
  const displayHeight = displayWidth / aspectRatio;

  // Initialize with existing analysis data if available
  const [analysisData, setAnalysisData] = useState<{
    segmentation?: Segmentation;
    pith?: Pith;
    rings?: Rings;
  }>(capture?.analysis || {});

  const [analysisProgress, setAnalysisProgress] = useState({
    segmentation: !!capture?.analysis?.segmentation,
    pithDetection: !!capture?.analysis?.pith,
    ringDetection: !!capture?.analysis?.rings,
  });

  const [overlayVisibility, setOverlayVisibility] = useState({
    segmentation: true,
    pith: true,
    rings: true,
  });

  const handleRetryAnalysis = async () => {
    if (!capture) return;

    setIsAnalyzing(true);
    setError(null);
    setAnalysisProgress({ segmentation: false, pithDetection: false, ringDetection: false });

    try {
      // Step 1: Segmentation
      const segmentation = await segmentImage(capture.image_base64);
      setAnalysisProgress(p => ({ ...p, segmentation: true }));
      setAnalysisData({ segmentation });

      // Step 2: Pith Detection
      const pith = await detectPith(segmentation.imageBase64);
      setAnalysisProgress(p => ({ ...p, pithDetection: true }));
      setAnalysisData(prev => ({ ...prev, pith }));

      // Step 3: Ring Detection
      const rings = await detectRings(segmentation.imageBase64, pith.x, pith.y);
      setAnalysisProgress(p => ({ ...p, ringDetection: true }));

      const newAnalysis = {
        segmentation,
        pith,
        rings
      };

      // Save the updated analysis data
      await updateCapture({ ...capture, analysis: newAnalysis });

      setAnalysisData(newAnalysis);
    } catch (error) {
      console.error('Analysis failed:', error);
      setError('Analysis failed. Please try again.');
      setAnalysisProgress({ segmentation: false, pithDetection: false, ringDetection: false });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle title changes
  const handleUpdateTitle = async (newTitle: string) => {
    if (capture) {
      // Create an updated capture object with the new title
      const updatedCapture = { ...capture, title: newTitle };
      // Update the capture in the database
      await updateCapture(updatedCapture);
      // Optionally update local state if needed
      setTitle(newTitle);
    }
  };

  const loadCapture = async () => {
    if (id) {
      const data = await getCaptureById(id as string);
      if (data) {
        setCapture(data);
        setTitle(data.title);
        if (data.analysis) {
          setAnalysisData({
            segmentation: data.analysis.segmentation,
            pith: data.analysis.pith,
            rings: data.analysis.rings,
          });
          setAnalysisProgress({
            segmentation: !!data.analysis.segmentation,
            pithDetection: !!data.analysis.pith,
            ringDetection: !!data.analysis.rings,
          });
        }
      }
    }
  };

  useEffect(() => {
    loadCapture();
  });

  // Trigger analysis automatically if the optional query param "analyze" is "true"
  useEffect(() => {
    if (analyze === 'true' && capture && !capture.analysis) {
      handleRetryAnalysis();
    }
  }, [analyze, capture]);

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

  const formattedDate = new Date(Number(capture.timestamp)).toLocaleDateString('de-DE');

  return (
    <ScrollView className="flex-1">
      <View className="flex-1 p-4 gap-4">
        {/* Image Overlay Container */}
        <View>
          <View className="rounded-lg overflow-hidden items-center">
            <ImageOverlay
              uri={capture.image_base64}
              segmentation={analysisData.segmentation || capture.analysis?.segmentation}
              pith={analysisData.pith || capture.analysis?.pith}
              rings={analysisData.rings || capture.analysis?.rings}
              width={displayWidth}
              height={displayHeight}
              showSegmentation={overlayVisibility.segmentation}
              showPith={overlayVisibility.pith}
              showRings={overlayVisibility.rings}
            />
          </View>
        </View>

        {/* Overlay Controls */}
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Overlay Controls</CardTitle>
          </CardHeader>
          <CardContent className="flex-col gap-2">
            <View className="flex-row items-center gap-2">
              <Switch
                checked={overlayVisibility.segmentation}
                onCheckedChange={(checked) =>
                  setOverlayVisibility(prev => ({ ...prev, segmentation: checked }))
                }
                nativeID="segmentation-toggle"
              />
              <Label nativeID="segmentation-toggle">Show Segmentation</Label>
            </View>
            <View className="flex-row items-center gap-2">
              <Switch
                checked={overlayVisibility.pith}
                onCheckedChange={(checked) =>
                  setOverlayVisibility(prev => ({ ...prev, pith: checked }))
                }
                nativeID="pith-toggle"
              />
              <Label nativeID="pith-toggle">Show Pith</Label>
            </View>
            <View className="flex-row items-center gap-2">
              <Switch
                checked={overlayVisibility.rings}
                onCheckedChange={(checked) =>
                  setOverlayVisibility(prev => ({ ...prev, rings: checked }))
                }
                nativeID="rings-toggle"
              />
              <Label nativeID="rings-toggle">Show Rings</Label>
            </View>
          </CardContent>
        </Card>

        {/* Content Container */}
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Capture Details</CardTitle>
          </CardHeader>
          <CardContent>
            <Input
              value={title}
              onChangeText={handleUpdateTitle}
              className="mb-4 pl-4"
              style={{ width: 250 }}
            />
            <View className="flex-row items-center gap-4">
              <Label className="text-lg">Captured</Label>
              <Text>{formattedDate}</Text>
            </View>
            <View className="flex-row items-center gap-4">
              <Label className="text-lg">Predicted Age</Label>
              <Text>{capture.analysis?.predictedAge ?? 'N/A'}</Text>
            </View>
          </CardContent>
        </Card>

        {/* Analysis Progress */}
        <View className="flex-1 gap-2 mt-4">
          {isAnalyzing ? (
            <View className="items-center py-4 gap-4">
              <Text className="text-lg font-semibold">Analysis Progress</Text>
              <View className="flex-row gap-4">
                <ProgressStep label="Segmentation" active={analysisProgress.segmentation} />
                <ProgressStep label="Pith Detection" active={analysisProgress.pithDetection} />
                <ProgressStep label="Ring Detection" active={analysisProgress.ringDetection} />
              </View>
              {error && <Text className="text-destructive">{error}</Text>}
            </View>
          ) : (
            <View className="flex-1">
              <View className="flex-row justify-start gap-4">
                <Button variant="outline" onPress={handleRetryAnalysis}>
                  <Text>Retry Analysis</Text>
                </Button>

                <Dialog>
                  <DialogTrigger asChild>
                    <Button className="flex-initial" variant="destructive">
                      <Text>Delete</Text>
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
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
                        variant="destructive"
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