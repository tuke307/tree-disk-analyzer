import { fetch } from 'expo/fetch';
import { EXPO_PUBLIC_API_URL } from '@/lib/constants/api';
import { arrayBufferToBase64, base64ToBlob, blobToBase64, completeBase64Data } from '@/lib/utils/image';
import axios from 'axios';

export async function healthCheck() {
  try {
    const response = await fetch(`${EXPO_PUBLIC_API_URL}/health`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

export async function segmentImage(base64: string): Promise<string> {
  const formData = new FormData();

  try {
    const blob = await base64ToBlob(base64);
    formData.append('image', blob, "active_contour_ac6_very_small.png");

    console.log(
      'Sending image to API for segmentation:',
      `${EXPO_PUBLIC_API_URL}/segmentation/image`
    );

    const response = await fetch(`${EXPO_PUBLIC_API_URL}/segmentation/image`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    console.log('API response:', response);
    const arrayBuffer = await response.arrayBuffer();
    console.log('Array buffer:', arrayBuffer.byteLength);
    const base64Image = arrayBufferToBase64(arrayBuffer);
    console.log('Base64 image:', base64Image.length);

    return completeBase64Data(base64Image);
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

export async function detectPith(base64: string): Promise<{ x: number; y: number }> {
  try {
    const formData = new FormData();
    formData.append('image', await base64ToBlob(base64));

    const response = await fetch(`${EXPO_PUBLIC_API_URL}/pith/detect`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}

export async function detectRings(
  base64: string,
  cx: number,
  cy: number
): Promise<string> {
  try {
    const formData = new FormData();
    formData.append('image', await base64ToBlob(base64));

    const response = await fetch(`${EXPO_PUBLIC_API_URL}/rings/detect?cx=${cx}&cy=${cy}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    const base64Image = arrayBufferToBase64(arrayBuffer);

    return completeBase64Data(base64Image);
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}
