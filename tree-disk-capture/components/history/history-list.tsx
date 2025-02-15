import { FlatList, View } from 'react-native';
import { HistoryItem } from '@/components/history/history-item';
import { CaptureWithAnalysis } from '@/lib/database/models';

interface Props {
  captures: CaptureWithAnalysis[];
}

export function HistoryList({ captures }: Props) {
  return (
    <FlatList
      className='flex-1'
      data={captures}
      keyExtractor={(item) => item.id.toString()}
      renderItem={({ item }) => <HistoryItem capture={item} />}
      ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
    />
  );
}