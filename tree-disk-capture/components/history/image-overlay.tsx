import React, { useEffect, useState } from 'react';
import { Canvas, Circle, Image, Skia, SkImage, useImage } from "@shopify/react-native-skia";
import { Dimensions, View } from 'react-native';
import { ImagePith, RingsDetection, SegmentationResult } from '@/lib/constants/types';

interface ImageOverlayProps {
    uri: string;
    segmentation?: SegmentationResult;
    pith?: ImagePith;
    rings?: RingsDetection;
    width: number;
    height: number;
    showSegmentation?: boolean;
    showPith?: boolean;
    showRings?: boolean;
}
const loadSkiaImage = async (uri: string): Promise<SkImage | null> => {
    let data;
    if (uri.startsWith('data:')) {
        // Remove the 'data:image/xxx;base64,' header
        const base64Str = uri.split(',')[1];
        data = Skia.Data.fromBase64(base64Str);
    } else {
        data = await Skia.Data.fromURI(uri);
    }
    return Skia.Image.MakeImageFromEncoded(data);
};

export const ImageOverlay = ({ 
    uri, 
    segmentation, 
    pith, 
    rings, 
    width, 
    height,
    showSegmentation = true,
    showPith = true,
    showRings = true 
}: ImageOverlayProps) => {
    const [image, setImage] = useState<SkImage | null>(null);
    const [maskImage, setMaskImage] = useState<SkImage | null>(null);

    useEffect(() => {
        const loadImages = async () => {
            const img = await loadSkiaImage(uri);
            
            if (!img || !segmentation || !segmentation.maskUri) return;

            const mImg = await loadSkiaImage(segmentation.maskUri);

            setImage(img);
            setMaskImage(mImg);
        };

        loadImages();
    }, [uri, segmentation]);

    if (!image || !segmentation) return null;

    // Use original dimensions instead of screen width
    const scaleFactor = 1; // Since we're using original dimensions

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
                        cx={pith.x}
                        cy={pith.y}
                        r={6}
                        color="rgba(255, 0, 0, 0.8)"
                    />
                )}

                {/* Growth Rings */}
                {rings && showRings && rings.rings.map((ring, index) => (
                    <Circle
                        key={`ring-${index}`}
                        cx={pith?.x ?? 0}
                        cy={pith?.y ?? 0}
                        r={ring.radius}
                        color="rgba(0, 255, 0, 0.5)"
                        style="stroke"
                        strokeWidth={2}
                    />
                ))}
            </Canvas>
        </View>
    );
};