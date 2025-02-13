import { View } from 'react-native';
import { HistoryItem } from '@/components/history/history-item';
import { Capture } from '@/lib/database/models';

interface Props {
  captures: Capture[];
}

export function HistoryList({ captures }: Props) {
  return (
    <View className='flex-1 w-full gap-2'>
      {captures.map((capture) => (
        <HistoryItem key={capture.id} capture={capture} />
      ))}
    </View>
  );
}