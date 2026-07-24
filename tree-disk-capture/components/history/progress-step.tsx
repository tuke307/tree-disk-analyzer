import { Icon } from '@/components/ui/icon';
import { ActivityIndicator, View } from 'react-native';
import { Button } from '../ui/button';
import { Text } from '../ui/text';
import { CheckIcon, XIcon } from 'lucide-react-native';


interface ProgressStepProps {
  label: string;
  loading: boolean;
  success?: boolean;
}

export const ProgressStep = ({ label, loading, success }: ProgressStepProps) => {
  return (
    <View className="flex flex-row items-center gap-2">
      <Button
        variant="ghost"
        size="icon">
        {/* 
          If loading is true, we only show the ActivityIndicator
          If loading is false, we check success to determine whether to show the CheckIcon or XIcon 
        */}
        {loading ? (
          <ActivityIndicator />
        ) : (
          success ? <Icon as={CheckIcon} className='text-foreground' /> : <Icon as={XIcon} className='text-foreground' />
        )}
      </Button>
      <Text>{label}</Text>
    </View>
  );
};