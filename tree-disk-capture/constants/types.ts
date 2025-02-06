export interface CaptureData {
    id: string;
    uri: string;
    timestamp: string;
    analysis: {
      predictedAge: number;
      predictedLocation: string;
    };
  }
  