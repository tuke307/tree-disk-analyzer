import { Button } from '@/components/ui/button';
import { Stack } from 'expo-router';
import { ArrowLeftIcon } from '@/lib/icons/ArrowLeftIcon';

export default function HistoryLayout() {
  return (
    <Stack
      screenOptions={({ navigation }) => ({
        headerLeft: () => (
          <Button variant="ghost" size="icon" onPress={() => navigation.goBack()}>
            <ArrowLeftIcon />
          </Button>
        ),
      })}
    />
  );
}