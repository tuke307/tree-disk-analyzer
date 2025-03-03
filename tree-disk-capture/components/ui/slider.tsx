import * as React from 'react';
import { View } from 'react-native';
import OriginalSlider, { SliderProps as OriginalSliderProps } from '@react-native-community/slider';
import { cn } from '@/lib/utils/ui';

type SliderProps = Omit<OriginalSliderProps, 'ref'> & {
    className?: string;
};


const Slider = React.forwardRef<React.ElementRef<typeof View>, SliderProps>(
    ({ className, style, minimumTrackTintColor, maximumTrackTintColor, thumbTintColor, ...props }, ref) => {

        return (
            <View ref={ref} className={cn('w-full', className)}>
                <OriginalSlider
                    className=''
                    style={[{ height: 40 }, style]}
                    minimumTrackTintColor={minimumTrackTintColor || cn("bg-primary")}
                    maximumTrackTintColor={maximumTrackTintColor || cn("bg-secondary")}
                    thumbTintColor={thumbTintColor || cn("bg-primary")}
                    {...props}
                />
            </View>
        );
    }
);

Slider.displayName = 'Slider';

export { Slider };
export type { SliderProps };
