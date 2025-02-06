import { View } from 'react-native';
import { HistoryItem } from './history-item';
import { CaptureData } from '@/lib/constants/types';

interface Props {
  captures: CaptureData[];
}

export function HistoryList({ captures }: Props) {
  return (
    <View>
      {captures.map((capture) => (
        <HistoryItem key={capture.id} capture={capture} />
      ))}
    </View>
  );
}