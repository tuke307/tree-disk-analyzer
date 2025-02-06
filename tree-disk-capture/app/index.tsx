import { View, ScrollView } from 'react-native';
import { router } from 'expo-router';
import { HistoryList } from '@/components/history/history-list';
import { NewCaptureButton } from '@/components/buttons/new-capture-button';
import { useCaptures } from '@/lib/hooks/use-captures';
import { Label } from '@/components/ui/label';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export default function Home() {
  const { captures } = useCaptures();
  const insets = useSafeAreaInsets();

  return (
    <View className="flex-1 m-4" style={{ paddingTop: insets.top }}>
      <View className="h-1/3">
        <NewCaptureButton onPress={() => router.push('/capture')} />
      </View>

      <View className="flex-1">
        <ScrollView className="flex-1">
          <View className="mt-4">
            <Label className="text-xl font-bold mb-4">History</Label>
            <HistoryList captures={captures} />
          </View>
        </ScrollView>
      </View>
    </View>
  );
}