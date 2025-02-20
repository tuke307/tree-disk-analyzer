import { CheckIcon } from '@/lib/icons/CheckIcon';
import { ActivityIndicator, View } from 'react-native';
import { Button } from '../ui/button';
import { Text } from '../ui/text';


interface ProgressStepProps {
  label: string;
  active: boolean;
}

export const ProgressStep = ({ label, active }: ProgressStepProps) => {
  return (
    <View className="items-center gap-2">
      <Button
        variant="ghost"
        size="icon">
        {active ? <ActivityIndicator /> : <CheckIcon />}
      </Button>
      <Text>{label}</Text>
    </View>
  );
};