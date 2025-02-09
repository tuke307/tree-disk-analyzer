import { AnalysisResult, ImagePith, RingsDetection, SegmentationResult } from './types';

const API_URL = 'http://127.0.0.1:8000';

export async function analyzeImage(uri: string): Promise<AnalysisResult> {
  await healthCheck();
  
  // Step 1: Segment image
  const segmentation = await segmentImage(uri);
  
  // Step 2: Detect pith
  const pith = await detectPith(segmentation.maskUri);
  
  // Step 3: Detect rings
  //const rings = await detectRings(uri, segmentation.maskUri, pith.x, pith.y);

  return {
    predictedAge: undefined, 
    segmentation,
    pith,
    rings: undefined,
  };
}

export async function healthCheck() {
  try {
    const response = await fetch(`${API_URL}/health`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

export async function segmentImage(uri: string): Promise<SegmentationResult> {
  try {
    const blob = base64ToBlob(uri);

    const formData = new FormData();
    formData.append('image', blob);

    const response = await fetch(`${API_URL}/segmentation/image`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const imageBlob = await response.blob();
    const base64Image = await blobToBase64(imageBlob);

    return {
      maskUri: base64Image,
    };
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

export async function detectPith(maskUri: string): Promise<ImagePith> {
  try {
    const formData = new FormData();
    formData.append('image', base64ToBlob(maskUri));

    const response = await fetch(`${API_URL}/pith/detect`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json() as ImagePith;
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

export async function detectRings(
  maskUri: string,
  cx: number,
  cy: number
): Promise<RingsDetection> {
  try {
    const formData = new FormData();
    formData.append('image', base64ToBlob(maskUri));

    const response = await fetch(`${API_URL}/rings/detect?cx=${cx}&cy=${cy}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const imageBlob = await response.blob();
    const base64Image = await blobToBase64(imageBlob);

    return {
      ringsUri: base64Image,
    };
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

function base64ToBlob(dataURL: string): Blob {
  const parts = dataURL.split(',');
  const byteString = atob(parts[1]);
  const mimeString = parts[0].split(':')[1].split(';')[0];

  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
  }

  return new Blob([ab], { type: mimeString });
}

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}