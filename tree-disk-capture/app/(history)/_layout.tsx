import { Button } from '@/components/ui/button';
import { Stack, useRouter } from 'expo-router';
import { Icon } from '@/components/ui/icon';
import { ArrowLeftIcon } from 'lucide-react-native';

export default function HistoryLayout() {
  const router = useRouter();

  const handleBack = () => {
    router.replace('/');
  };

  return (
    <Stack
      screenOptions={{
        headerLeft: () => (
          <Button
            variant="ghost"
            size="icon"
            onPress={handleBack}
          >
            <Icon as={ArrowLeftIcon} className='text-foreground' />
          </Button>
        ),
      }}
    />
  );
}