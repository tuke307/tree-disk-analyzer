import { CaptureWithAnalysis, NewCapture } from '@/lib/database/models';
import { create } from 'zustand'

type WebCaptureStore = {
    captures: CaptureWithAnalysis[];
    addCapture: (capture: NewCapture) => CaptureWithAnalysis;
    updateCapture: (capture: CaptureWithAnalysis) => void;
    deleteCapture: (id: string) => void;
    getCaptureById: (id: string) => CaptureWithAnalysis | undefined;
    loadCaptures: () => Promise<CaptureWithAnalysis[]>;
};

export const useWebCaptureStore = create<WebCaptureStore>((set, get) => ({
    captures: [],
    addCapture: (newCapture) => {
        const now = new Date();

        const capture: CaptureWithAnalysis = {
            ...newCapture,
            id: Math.random().toString(),
            createdAt: now.toISOString(),
            updatedAt: now.toISOString(),
            title: 'Analysis ' + now.toLocaleString("de-DE"),
            analysisId: null,
            analysis: undefined,
        };
        set({ captures: [...get().captures, capture] });
        return capture;
    },
    updateCapture: (updatedCapture) => {
        set((state) => ({
            captures: state.captures.map((c) =>
                c.id === updatedCapture.id ? updatedCapture : c
            )
        }));

        return updatedCapture;
    },
    deleteCapture: (id) => {
        set((state) => ({
            captures: state.captures.filter((c) => c.id !== id)
        }));
    },
    getCaptureById: (id) => get().captures.find((c) => c.id === id),
    loadCaptures: async () => {
        return get().captures;
    }
}));

export function useCaptures() {
    return useWebCaptureStore();
}