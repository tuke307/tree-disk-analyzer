import React, { useEffect, useState } from 'react';
import { Canvas, Circle, Image, Skia, SkImage, useImage } from "@shopify/react-native-skia";
import { Dimensions, View } from 'react-native';
import { ImagePith, RingsDetection, SegmentationResult } from '@/lib/constants/types';

interface ImageOverlayProps {
    uri: string;
    segmentation?: SegmentationResult;
    pith?: ImagePith;
    rings?: RingsDetection;
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

export const ImageOverlay = ({ uri, segmentation, pith, rings }: ImageOverlayProps) => {
    const [image, setImage] = useState<SkImage | null>(null);
    const [maskImage, setMaskImage] = useState<SkImage | null>(null);

    const screenWidth = Dimensions.get('window').width;

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

    // Calculate scaling factors
    const imageAspectRatio = image.width() / image.height();
    const displayHeight = screenWidth / imageAspectRatio;
    const scaleFactor = screenWidth / image.width();

    return (
        <View style={{ width: screenWidth, height: displayHeight }}>
            <Canvas style={{ flex: 1 }}>
                {/* Base Image */}
                <Image
                    image={image}
                    fit="contain"
                    rect={{ x: 0, y: 0, width: screenWidth, height: displayHeight }}
                />

                {/* Segmentation Mask Overlay */}
                {maskImage && (
                    <Image
                        image={maskImage}
                        fit="contain"
                        rect={{ x: 0, y: 0, width: screenWidth, height: displayHeight }}
                        opacity={0.4}
                    />
                )}

                {/* Pith Point */}
                {pith && (
                    <Circle
                        cx={pith.x * scaleFactor}
                        cy={pith.y * scaleFactor}
                        r={6}
                        color="rgba(255, 0, 0, 0.8)"
                    />
                )}

                {/* Growth Rings */}
                {rings?.rings.map((ring, index) => (
                    <Circle
                        key={`ring-${index}`}
                        cx={pith?.x ? pith.x * scaleFactor : 0}
                        cy={pith?.y ? pith.y * scaleFactor : 0}
                        r={ring.radius * scaleFactor}
                        color="rgba(0, 255, 0, 0.5)"
                        style="stroke"
                        strokeWidth={2}
                    />
                ))}
            </Canvas>
        </View>
    );
};