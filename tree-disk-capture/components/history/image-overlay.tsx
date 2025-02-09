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
    const [ringsImage, setRingsImage] = useState<SkImage | null>(null);


    useEffect(() => {
        const loadImages = async () => {
            if (uri) {
                const img = await loadSkiaImage(uri);
                if (img) {
                    setImage(img);
                }
            }

            if (segmentation && segmentation.maskUri) {
                const mImg = await loadSkiaImage(segmentation.maskUri);
                if (mImg) {
                    setMaskImage(mImg);
                }
            }

            if (rings && rings.ringsUri) {
                const rImg = await loadSkiaImage(rings.ringsUri);
                if (rImg) {
                    setRingsImage(rImg);
                }
            }
        };

        loadImages();
    }, [uri, segmentation]);

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