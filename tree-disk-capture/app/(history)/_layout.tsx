import { Button } from '@/components/ui/button';
import { Stack, useRouter } from 'expo-router';
import { ArrowLeftIcon } from '@/lib/icons/ArrowLeftIcon';

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
            <ArrowLeftIcon className='text-foreground' />
          </Button>
        ),
      }}
    />
  );
}