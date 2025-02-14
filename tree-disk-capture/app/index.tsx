import { useCallback, useEffect } from 'react';
import { View, ScrollView } from 'react-native';
import { router, useFocusEffect } from 'expo-router';
import { HistoryList } from '@/components/history/history-list';
import { NewCaptureButton } from '@/components/buttons/new-capture-button';
import { useCaptures } from '@/lib/hooks/use-captures';
import { Text } from '@/components/ui/text';
import { useSafeAreaInsets } from 'react-native-safe-area-context';


export default function Home() {
  const { captures, loadCaptures } = useCaptures();
  const insets = useSafeAreaInsets();

  useEffect(() => {
    loadCaptures();
  }, []); // no dependencies, only run once

  return (
    <View className="flex-1 m-4" style={{ paddingTop: insets.top }}>
      <View className="h-1/3">
        <NewCaptureButton onPress={() => router.push('/capture')} />
      </View>

      <View className="flex-1 mt-8">
        <ScrollView className="flex-1">
          <View>
            <Text className="text-xl font-bold mb-4">History</Text>
            <HistoryList captures={captures} />
          </View>
        </ScrollView>
      </View>
    </View>
  );
}