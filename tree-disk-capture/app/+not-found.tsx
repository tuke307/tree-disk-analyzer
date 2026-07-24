import { Button } from '@/components/ui/button';
import { Text } from '@/components/ui/text';
import { Stack, useRouter } from 'expo-router';
import { View } from 'react-native';

export default function NotFoundScreen() {
  const router = useRouter();

  return (
    <View className="flex-1">
      <Stack.Screen options={{ title: 'Oops!' }} />
      <View className="flex-1 gap-4 items-center justify-center p-5">
        <Text variant="h1">This screen doesn't exist.</Text>

        <Button variant="outline" onPress={() => router.replace('/')}>
          <Text>Go to home screen!</Text>
        </Button>
      </View>
    </View>
  );
}
