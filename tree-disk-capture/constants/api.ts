export async function analyzeImage(uri: string) {
    // Replace with your actual API endpoints
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