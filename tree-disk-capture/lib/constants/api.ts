export async function analyzeImage(uri: string) {

  // return demo data
  return {
    predictedAge: 42,
  };


  try {
    const response = await fetch('YOUR_API_ENDPOINT', {
      method: 'POST',
      body: JSON.stringify({ uri }),
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return await response.json();
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
}