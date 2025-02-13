export function completeBase64Data(base64: string, uri?: string): string {
    // If the base64 string already starts with the data URI scheme, return it as-is.
    if (base64.startsWith("data:image/")) {
        return base64;
    }

    // Extract the file extension from the URI.
    const extensionMatch = uri?.match(/\.([a-zA-Z0-9]+)$/);
    let extension = "png"; // default extension

    if (extensionMatch && extensionMatch[1]) {
        extension = extensionMatch[1].toLowerCase();
        if (extension === "jpg") {
            // Normalize jpg to jpeg.
            extension = "jpeg";
        }
    }

    // Construct and return the complete base64 data URL.
    return `data:image/${extension};base64,${base64}`;
}

export async function base64ToBlob(base64: string): Promise<Blob> {
    const response = await fetch(base64);
    return await response.blob();
}

export function blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

export function arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    const chunkSize = 0x8000; // 32768
    let binary = '';
    for (let i = 0; i < bytes.length; i += chunkSize) {
        const chunk = bytes.subarray(i, i + chunkSize);
        binary += String.fromCharCode.apply(null, Array.from(chunk));
    }
    return btoa(binary);
}