import { View, ScrollView, Text } from 'react-native';
import { router } from 'expo-router';
import { HistoryList } from '@/components/history/history-list';
import { NewCaptureButton } from '@/components/buttons/new-capture-button';
import { useCaptures } from '@/hooks/use-captures';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';

export default function Home() {
  const { captures } = useCaptures();

  return (
    <ThemedView className="flex-1 bg-gray-900">
      <NewCaptureButton onPress={() => router.push('/capture')} />
      <ThemedView className="flex-1">
        <ScrollView className="flex-1">
          <ThemedView className="p-4">
            <ThemedText className="text-white text-xl font-bold mb-4">History</ThemedText>
            <HistoryList captures={captures} />
          </ThemedView>
        </ScrollView>
      </ThemedView>
    </ThemedView>
  );
}