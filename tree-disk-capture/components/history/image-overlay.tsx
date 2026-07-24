import React from 'react';
import { Canvas, Circle, Image, useImage } from "@shopify/react-native-skia";
import { View } from 'react-native';
import { Pith, Rings, Segmentation } from '@/lib/database/models';

interface ImageOverlayProps {
    imageBase64: string;
    segmentation?: Segmentation;
    pith?: Pith;
    rings?: Rings;
    width: number;
    height: number;
    showSegmentation?: boolean;
    showPith?: boolean;
    showRings?: boolean;
}

export const ImageOverlay = ({
    imageBase64,
    segmentation,
    pith,
    rings,
    width,
    height,
    showSegmentation = true,
    showPith = true,
    showRings = true
}: ImageOverlayProps) => {
    const image = useImage(imageBase64 || null);
    const maskImage = useImage(segmentation?.imageBase64 || null);
    const ringsImage = useImage(rings?.imageBase64 || null);

    // Compute scaling ratios if image is loaded.
    const scaleX = image ? width / image.width() : 1;
    const scaleY = image ? height / image.height() : 1;

    return (
        <View style={{ width, height }}>
            <Canvas style={{ flex: 1 }}>
                {/* Base Image */}
                <Image
                    image={image}
                    fit="contain"
                    rect={{ x: 0, y: 0, width, height }}
                />

                {/* Segmentation Mask Overlay */}
                {maskImage && showSegmentation && (
                    <Image
                        image={maskImage}
                        fit="contain"
                        rect={{ x: 0, y: 0, width, height }}
                        opacity={0.4}
                    />
                )}

                {/* Pith Point */}
                {pith && showPith && (
                    <Circle
                        cx={pith.x * scaleX}
                        cy={pith.y * scaleY}
                        r={6}
                        color="rgba(255, 0, 0, 0.8)"
                    />
                )}

                {/* Growth Rings Mask Overlay */}
                {rings && showRings && (
                    <Image
                        image={ringsImage}
                        fit="contain"
                        rect={{ x: 0, y: 0, width, height }}
                        opacity={0.4}
                    />
                )}
            </Canvas>
        </View>
    );
};