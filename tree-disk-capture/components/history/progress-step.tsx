import { cn } from '@/lib/utils/ui';
import { View, Text } from 'react-native';


interface ProgressStepProps {
  label: string;
  active: boolean;
}

export const ProgressStep = ({ label, active }: ProgressStepProps) => {
  return (
    <View className="items-center gap-2">
      <View className={cn(
        "w-8 h-8 rounded-full items-center justify-center",
        active ? "bg-green-500" : "bg-gray-300"
      )}>
        <Text className="font-bold">{active ? '✓' : '?'}</Text>
      </View>
      <Text>{label}</Text>
    </View>
  );
};