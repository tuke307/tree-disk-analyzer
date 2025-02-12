import { Analysis, Pith, Rings, Segmentation } from '@/lib/database/models';
import { API_URL } from '@/lib/constants/api';


export async function analyzeImage(uri: string): Promise<Analysis> {
  await healthCheck();
  
  // Step 1: Segment image
  const segmentation = await segmentImage(uri);
  
  // Step 2: Detect pith
  const pith = await detectPith(segmentation.imageBase64);
  
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

export async function segmentImage(uri: string): Promise<Segmentation> {
  try {
    const formData = new FormData();
    formData.append('image', await base64ToBlob(uri));

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
      imageBase64: base64Image,
    };
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

export async function detectPith(maskUri: string): Promise<Pith> {
  try {
    const formData = new FormData();
    formData.append('image', await base64ToBlob(maskUri));

    const response = await fetch(`${API_URL}/pith/detect`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json() as Pith;
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

export async function detectRings(
  maskUri: string,
  cx: number,
  cy: number
): Promise<Rings> {
  try {
    const formData = new FormData();
    formData.append('image', await base64ToBlob(maskUri));

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
      imageBase64: base64Image,
    };
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

async function base64ToBlob(dataURL: string): Promise<Blob> {
  const response = await fetch(dataURL);
  return await response.blob();
}

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}