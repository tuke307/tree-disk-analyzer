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
import Slider from '@react-native-community/slider';

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
    //th_l: 5.0,
    //th_h: 20.0,
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

  const [loadingProgress, setLoadingProgress] = useState({
    segmentation: false,
    pithDetection: false,
    ringDetection: false,
  });

  const [overlayVisibility, setOverlayVisibility] = useState({
    segmentation: true,
    pith: true,
    rings: true,
  });

  const handleSegmentation = async () => {
    if (!capture) return;

    setIsAnalyzing(true);
    setError(null);
    setLoadingProgress(prev => ({ ...prev, segmentation: true }));

    const newAnalysis: any = {
      ...capture.analysis
    };

    try {
      console.log('Starting segmentation for capture:', capture.id);

      // Segmentation
      const segBase64Image = await segmentImage(capture.imageBase64);
      newAnalysis.segmentation = {
        ...capture.analysis?.segmentation,
        imageBase64: segBase64Image
      };

      const currentCapture: CaptureWithAnalysis = { ...capture, analysis: newAnalysis };
      const savedCapture = await updateCapture(currentCapture);
      if (savedCapture && savedCapture.analysis) {
        setCapture(savedCapture);
        setAnalysisData(savedCapture.analysis || newAnalysis);
      }
    } catch (error) {
      console.error('Segmentation failed:', error);
      setError('Segmentation failed. Please try again.');
    } finally {
      setLoadingProgress(prev => ({ ...prev, segmentation: false }));
      setIsAnalyzing(false);
    }
  };

  const handlePithDetection = async () => {
    if (!capture || !capture.analysis?.segmentation?.imageBase64) {
      setError('Segmentation must be completed first.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setLoadingProgress(prev => ({ ...prev, pithDetection: true }));

    const newAnalysis: any = {
      ...capture.analysis
    };

    try {
      console.log('Starting pith detection for capture:', capture.id);

      // Pith Detection
      const pithData = await detectPith(capture.analysis.segmentation.imageBase64);
      newAnalysis.pith = {
        ...capture.analysis?.pith,
        x: pithData.x,
        y: pithData.y
      };

      const currentCapture: CaptureWithAnalysis = { ...capture, analysis: newAnalysis };
      const savedCapture = await updateCapture(currentCapture);
      if (savedCapture && savedCapture.analysis) {
        setCapture(savedCapture);
        setAnalysisData(savedCapture.analysis || newAnalysis);
      }
    } catch (error) {
      console.error('Pith detection failed:', error);
      setError('Pith detection failed. Please try again.');
    } finally {
      setLoadingProgress(prev => ({ ...prev, pithDetection: false }));
      setIsAnalyzing(false);
    }
  };

  const handleRingDetection = async () => {
    if (!capture || !capture.analysis?.segmentation?.imageBase64) {
      setError('Segmentation must be completed first.');
      return;
    }

    if (!capture.analysis?.pith) {
      setError('Pith detection must be completed first.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setLoadingProgress(prev => ({ ...prev, ringDetection: true }));

    const newAnalysis: any = {
      ...capture.analysis
    };

    try {
      console.log('Starting ring detection for capture:', capture.id);

      // Ring Detection
      const { age, base64 } = await detectRings(
        capture.analysis.segmentation.imageBase64,
        capture.analysis.pith.x,
        capture.analysis.pith.y,
        edgeParams.sigma
      );
      newAnalysis.rings = {
        ...capture.analysis?.rings,
        imageBase64: base64
      };
      newAnalysis.predictedAge = age;

      const currentCapture: CaptureWithAnalysis = { ...capture, analysis: newAnalysis };
      const savedCapture = await updateCapture(currentCapture);
      if (savedCapture) {
        setCapture(savedCapture);
        setAnalysisData(savedCapture.analysis || newAnalysis);
      }
    } catch (error) {
      console.error('Ring detection failed:', error);
      setError('Ring detection failed. Please try again.');
    } finally {
      setLoadingProgress(prev => ({ ...prev, ringDetection: false }));
      setIsAnalyzing(false);
    }
  };

  const handleRetryAnalysis = async () => {
    if (!capture) return;

    setIsAnalyzing(true);
    setError(null);
    setLoadingProgress({ segmentation: true, pithDetection: true, ringDetection: true });

    // Set analyze query parameter when starting analysis
    router.setParams({ analyze: 'true' });

    try {
      await handleSegmentation();
      if (capture.analysis?.segmentation) {
        await handlePithDetection();
        if (capture.analysis?.pith) {
          await handleRingDetection();
        }
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setError('Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);

      // Reset loading progress
      setLoadingProgress({
        segmentation: false,
        pithDetection: false,
        ringDetection: false,
      });

      // Reset analyze query parameter when analysis is complete
      router.setParams({ analyze: undefined });
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
    if (analyze === 'true' && capture && !capture.analysis && !isAnalyzing) {
      handleRetryAnalysis();
    }
  }, [analyze, capture, isAnalyzing]);

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
              imageBase64={capture.imageBase64}
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

        {/* Overlay Controls */}
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Overlay Controls</CardTitle>
          </CardHeader>
          <CardContent className="flex-col gap-3">
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
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Analysis</CardTitle>
          </CardHeader>
          <CardContent className='flex-col gap-4'>
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
                            <Text>Controls smoothing. Increase for detailled, high-contrast images, decrease for smoother, low-contrast images.</Text>
                          </TooltipContent>
                        </Tooltip>
                      </View>

                      <Slider
                        minimumValue={0}
                        maximumValue={6}
                        step={0.1}
                        value={edgeParams.sigma}
                        onValueChange={(value) =>
                          setEdgeParams(prev => ({
                            ...prev,
                            sigma: value,
                          }))
                        }
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

            {/* Progress Steps */}
            <View className="flex-col gap-2">
              <View className="flex-row items-center gap-4">
                <ProgressStep
                  label="Segmentation"
                  loading={loadingProgress.segmentation}
                  success={!!capture?.analysis?.segmentation}
                />
                <Button
                  variant="outline"
                  size="sm"
                  onPress={handleSegmentation}
                  disabled={isAnalyzing}>
                  <Text>Retry</Text>
                </Button>
              </View>

              <View className="flex-row items-center gap-4">
                <ProgressStep
                  label="Pith Detection"
                  loading={loadingProgress.pithDetection}
                  success={!!capture.analysis?.pith}
                />
                <Button
                  variant="outline"
                  size="sm"
                  onPress={handlePithDetection}
                  disabled={isAnalyzing}>
                  <Text>Retry</Text>
                </Button>
              </View>

              <View className="flex-row items-center gap-4">
                <ProgressStep
                  label="Ring Detection"
                  loading={loadingProgress.ringDetection}
                  success={!!capture.analysis?.rings}
                />
                <Button
                  variant="outline"
                  size="sm"
                  onPress={handleRingDetection}
                  disabled={isAnalyzing}>
                  <Text>Retry</Text>
                </Button>
              </View>
            </View>

            {/* Error Message */}
            {error && <Text className="text-destructive">{error}</Text>}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <View className="flex-1 gap-2 mt-4">
          <View className="flex-1">
            <View className="flex-row justify-start gap-4">
              <Button variant="outline" onPress={handleRetryAnalysis} disabled={isAnalyzing}>
                <Text>Retry Analysis</Text>
              </Button>

              <Dialog>
                <DialogTrigger asChild>
                  <Button className="flex-initial" variant="destructive" disabled={isAnalyzing}>
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
        </View>
      </View>
    </ScrollView>
  );
}
