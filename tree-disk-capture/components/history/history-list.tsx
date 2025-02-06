import { View } from 'react-native';
import { HistoryItem } from './history-item';
import { CaptureData } from '@/constants/types';
import { ThemedView } from '../ThemedView';

interface Props {
  captures: CaptureData[];
}

export function HistoryList({ captures }: Props) {
  return (
    <ThemedView>
      {captures.map((capture) => (
        <HistoryItem key={capture.id} capture={capture} />
      ))}
    </ThemedView>
  );
}