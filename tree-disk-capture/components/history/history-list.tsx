import { View } from 'react-native';
import { HistoryItem } from '@/components/history/history-item';
import { Capture } from '@/lib/database/models';

interface Props {
  captures: Capture[];
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