import { Label } from '@/components/ui/label';
import { H1 } from '@/components/ui/typography';
import { Link, Stack } from 'expo-router';
import { View } from 'react-native';

export default function NotFoundScreen() {
  return (
    <View className="flex-1">
      <Stack.Screen options={{ title: 'Oops!' }} />
      <View className="flex-1 items-center justify-center p-5">
        <H1>This screen doesn't exist.</H1>
        <Link href="/" className="mt-4 py-4">
          <Label>Go to home screen!</Label>
        </Link>
      </View>
    </View>
  );
}
