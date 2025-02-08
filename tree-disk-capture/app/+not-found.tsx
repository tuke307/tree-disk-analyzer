import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { H1 } from '@/components/ui/typography';
import { Stack, useRouter } from 'expo-router';
import { View } from 'react-native';

export default function NotFoundScreen() {
  const router = useRouter();

  return (
    <View className="flex-1">
      <Stack.Screen options={{ title: 'Oops!' }} />
      <View className="flex-1 gap-4 items-center justify-center p-5">
        <H1>This screen doesn't exist.</H1>

        <Button variant="outline" onPress={() => router.replace('/')}>
          <Text>Go to home screen!</Text>
        </Button>
      </View>
    </View>
  );
}
