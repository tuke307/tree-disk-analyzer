import { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, Dimensions, Platform } from 'react-native';
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
import { AnalysisWithRelations, Capture, CaptureWithAnalysis } from '@/lib/database/models';
import { ProgressStep } from '@/components/history/progress-step';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { InfoIcon } from '@/lib/icons/InfoIcon';

export default function CaptureDetails() {
  const { id, analyze } = useLocalSearchParams();
  const navigation = useNavigation();
  const router = useRouter();
  const { getCaptureById, deleteCapture, updateCapture } = useCaptures();
  const insets = useSafeAreaInsets();

  const [capture, setCapture] = useState<CaptureWithAnalysis | null>(null);
  const [title, setTitle] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [edgeParams, setEdgeParams] = useState({
    sigma: 3.0,
    th_l: 5.0,
    th_h: 20.0,
  });

  // Calculate display dimensions based on screen width
  const screenWidth = Dimensions.get('window').width * 0.9; // 90% of screen width for padding
  const originalWidth = capture?.width || 800;
  const originalHeight = capture?.height || 600;
  const aspectRatio = originalWidth / originalHeight;
  const displayWidth = Math.min(originalWidth, screenWidth);
  const displayHeight = displayWidth / aspectRatio;

  // Initialize with existing analysis data if available
  const [analysisData, setAnalysisData] = useState<AnalysisWithRelations | null>(null);

  const [analysisProgress, setAnalysisProgress] = useState({
    segmentation: Boolean(capture?.analysis?.segmentation),
    pithDetection: Boolean(capture?.analysis?.pith),
    ringDetection: Boolean(capture?.analysis?.rings),
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

    const newAnalysis: any = {
      ...capture.analysis
    };

    try {
      console.log('Starting analysis for capture:', capture.id);

      // Step 1: Segmentation
      const segBase64Image = await segmentImage(capture.imageBase64);
      newAnalysis.segmentation = {
        ...capture.analysis?.segmentation,
        imageBase64: segBase64Image
      };
      setAnalysisProgress(prev => ({ ...prev, segmentation: true }));

      let currentCapture: CaptureWithAnalysis = { ...capture, analysis: newAnalysis };
      let savedCapture = await updateCapture(currentCapture);
      if (savedCapture && savedCapture.analysis) {
        setCapture(savedCapture);
        setAnalysisData(savedCapture.analysis || newAnalysis);
        currentCapture = savedCapture;

        // Update newAnalysis with latest IDs
        newAnalysis.id = savedCapture.analysis?.id;
        newAnalysis.segmentationId = savedCapture.analysis?.segmentationId;
      }

      // Step 2: Pith Detection
      const pithData = await detectPith(segBase64Image);
      newAnalysis.pith = {
        ...capture.analysis?.pith,
        x: pithData.x,
        y: pithData.y
      };
      setAnalysisProgress(prev => ({ ...prev, pithDetection: true }));

      currentCapture = { ...currentCapture, analysis: newAnalysis };
      savedCapture = await updateCapture(currentCapture);
      if (savedCapture && savedCapture.analysis) {
        setCapture(savedCapture);
        setAnalysisData(savedCapture.analysis || newAnalysis);
        currentCapture = savedCapture;
        
        // Update newAnalysis with latest IDs
        newAnalysis.pithId = savedCapture.analysis?.pithId;
      }

      // Step 3: Ring Detection
      const { age, base64 } = await detectRings(
        segBase64Image,
        pithData.x,
        pithData.y,
        edgeParams.sigma,
        edgeParams.th_l,
        edgeParams.th_h
      );
      newAnalysis.rings = {
        ...capture.analysis?.rings,
        imageBase64: base64
      };
      newAnalysis.predictedAge = age;
      setAnalysisProgress(prev => ({ ...prev, ringDetection: true }));

      currentCapture = { ...currentCapture, analysis: newAnalysis };
      savedCapture = await updateCapture(currentCapture);
      if (savedCapture) {
        setCapture(savedCapture);
        setAnalysisData(savedCapture.analysis || newAnalysis);
        currentCapture = savedCapture;
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setError('Analysis failed. Please try again.');
      setAnalysisProgress({ segmentation: false, pithDetection: false, ringDetection: false });
    } finally {
      console.log('Analysis complete:', newAnalysis.id);

      setIsAnalyzing(false);
    }
  };

  // Handle title changes
  const handleUpdateTitle = async (newTitle: string) => {
    if (capture) {
      const updatedCapture = { ...capture, title: newTitle };
      await updateCapture(updatedCapture);
      setTitle(newTitle);
    }
  };

  const loadCapture = async () => {
    if (!id) return;

    try {
      const data = await getCaptureById(id as string);
      if (data) {
        setCapture(data);
        setTitle(data.title);

        if (data.analysis) {
          const analysisData: AnalysisWithRelations = { ...data.analysis };

          setAnalysisData(analysisData);
          setAnalysisProgress({
            segmentation: !!data.analysis.segmentation,
            pithDetection: !!data.analysis.pith,
            ringDetection: !!data.analysis.rings,
          });
        } else {
          setAnalysisData(null);
        }
      }
    } catch (error) {
      console.error('Error loading capture:', error);
      setError('Failed to load capture');
    }
  };

  useEffect(() => {
    loadCapture();
  }, []); // no dependencies, only run once

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

  const captureCreatedAt = new Date(capture.createdAt).toLocaleDateString('de-DE');

  return (
    <ScrollView className="flex-1">
      <View className="flex-1 p-4 gap-4">
        {/* Image Overlay Container */}
        <View>
          <View className="rounded-lg overflow-hidden items-center">
            <ImageOverlay
              uri={capture.imageBase64}
              segmentation={analysisData?.segmentation || capture.analysis?.segmentation}
              pith={analysisData?.pith || capture.analysis?.pith}
              rings={analysisData?.rings || capture.analysis?.rings}
              width={displayWidth}
              height={displayHeight}
              showSegmentation={overlayVisibility.segmentation}
              showPith={overlayVisibility.pith}
              showRings={overlayVisibility.rings}
            />
          </View>
        </View>

        {/* Edge Detection Settings Popover */}
        <View className="items-start">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Text>Edge Detection Settings</Text>
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Edge Detection Settings</DialogTitle>
                <DialogDescription>
                  Adjust parameters for edge detection.
                </DialogDescription>
              </DialogHeader>

              <View className="flex-col gap-4">
                <View>
                  <View className="flex-row items-center">
                    <Label>Sigma</Label>
                    <Tooltip delayDuration={150}>
                      <TooltipTrigger asChild>
                        <Button variant='ghost' size="icon">
                          <InfoIcon size={16} className='text-foreground' />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent insets={insets}>
                        <Text>Controls smoothing. Increase for noisy images, decrease for detailed images.</Text>
                      </TooltipContent>
                    </Tooltip>
                  </View>

                  <Input
                    keyboardType="numeric"
                    value={edgeParams.sigma.toString()}
                    onChangeText={(text) =>
                      setEdgeParams(prev => ({
                        ...prev,
                        sigma: parseFloat(text) || 0,
                      }))
                    }
                    placeholder="sigma: default 3.0"
                  />
                </View>

                <View>
                  <View className="flex-row items-center">
                    <Label>Low Threshold</Label>
                    <Tooltip delayDuration={150}>
                      <TooltipTrigger asChild>
                        <Button variant='ghost' size="icon">
                          <InfoIcon size={16} className='text-foreground' />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent insets={insets}>
                        <Text>Helps connect weak edges. Typically set relative to th_h.</Text>
                      </TooltipContent>
                    </Tooltip>
                  </View>

                  <Input
                    keyboardType="numeric"
                    value={edgeParams.th_l.toString()}
                    onChangeText={(text) =>
                      setEdgeParams(prev => ({
                        ...prev,
                        th_l: parseFloat(text) || 0,
                      }))
                    }
                    placeholder="low threshold: default 5.0"
                  />
                </View>

                <View>
                  <View className="flex-row items-center">
                    <Label>High Threshold</Label>
                    <Tooltip delayDuration={150}>
                      <TooltipTrigger asChild>
                        <Button variant='ghost' size="icon">
                          <InfoIcon size={16} className='text-foreground' />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent insets={insets}>
                        <Text>Sets the bar for strong edges. Adjust based on image contrast.</Text>
                      </TooltipContent>
                    </Tooltip>
                  </View>

                  <Input
                    keyboardType="numeric"
                    value={edgeParams.th_h.toString()}
                    onChangeText={(text) =>
                      setEdgeParams(prev => ({
                        ...prev,
                        th_h: parseFloat(text) || 0,
                      }))
                    }
                    placeholder="high threshold: default 20.0"
                  />
                </View>
              </View>

              <DialogFooter>
                <DialogClose asChild>
                  <Button>
                    <Text>OK</Text>
                  </Button>
                </DialogClose>
              </DialogFooter>
            </DialogContent>
          </Dialog>
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

        {/* Capture Details */}
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
              <Text>{captureCreatedAt}</Text>
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
