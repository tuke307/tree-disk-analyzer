import { Stack } from 'expo-router';

export default function HistoryLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: '#1f2937' },
        headerTintColor: '#fff',
      }}
    />
  );
}