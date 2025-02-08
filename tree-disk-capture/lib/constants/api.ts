export async function analyzeImage(uri: string) {

  // return demo data
  const minAge = 1;
  const maxAge = 100;
  const predictedAge = Math.floor(Math.random() * (maxAge - minAge + 1)) + minAge;

  return {
    predictedAge
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