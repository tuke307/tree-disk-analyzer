export interface CaptureData {
  id: string;
  title: string;
  uri: string;
  timestamp: string;
  analysis: AnalysisResult | undefined;
  width: number;
  height: number;
}

export interface AnalysisResult {
  segmentation: SegmentationResult | undefined;
  pith: ImagePith | undefined;
  rings: RingsDetection | undefined;
  predictedAge: number | undefined;
}

export interface SegmentationResult {
  maskUri: string;
}

export interface ImagePith {
  x: number;
  y: number;
}

export interface RingsDetection {
  ringsUri: string;
}

export interface DemoData {
  capture: CaptureData;
  analysisSteps: {
    segmentation: SegmentationResult;
    pith: ImagePith;
    rings: RingsDetection;
  };
}