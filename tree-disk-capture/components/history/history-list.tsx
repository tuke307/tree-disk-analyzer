import { View } from 'react-native';
import { HistoryItem } from '@/components/history/history-item';
import { CaptureWithAnalysis } from '@/lib/database/models';

interface Props {
  captures: CaptureWithAnalysis[];
}

export function HistoryList({ captures }: Props) {
  return (
    <View className='flex-1 gap-2'>
      {captures.map((capture) => (
        <HistoryItem key={capture.id} capture={capture} />
      ))}
    </View>
  );
}