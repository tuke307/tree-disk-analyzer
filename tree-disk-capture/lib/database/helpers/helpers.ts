import type { Segmentation, Pith, Rings, Analysis, AnalysisWithRelations, Capture } from '@/lib/database/models';
import * as Crypto from 'expo-crypto';


export function createNewCapture(newCapture: Partial<Capture>): Capture {
  return {
    id: Crypto.randomUUID(),
    title: "analysis " + new Date().toLocaleString('de-DE'),
    timestamp: new Date().toISOString(),
    imageBase64: newCapture.imageBase64 ?? "",
    width: newCapture.width ?? 0,
    height: newCapture.height ?? 0,
    analysisId: newCapture.analysisId ?? null,
  };
}

export function createNewAnalysis(): AnalysisWithRelations {
  return {
    id: 0,
    predictedAge: null,
    segmentationId: null,
    pithId: null,
    ringsId: null,
  };
}

export function createNewSegmentation(imageBase64: string): Segmentation {
  return {
    id: 0,
    imageBase64,
  };
}

export function createNewPith(x: number, y: number): Pith {
  return {
    id: 0,
    x,
    y,
  };
}

export function createNewRings(imageBase64: string): Rings {
  return {
    id: 0,
    imageBase64,
  };
}