import { useState, useEffect } from 'react';
import { Capture, CaptureWithAnalysis, AnalysisWithRelations, Analysis } from '@/lib/database/models';
import * as schema from '@/lib/database/models';
import { drizzle } from 'drizzle-orm/expo-sqlite';
import { useSQLiteContext } from 'expo-sqlite';
import { eq } from 'drizzle-orm';
import { createNewCapture } from '../database/helpers/helpers';


type DrizzleDB = ReturnType<typeof drizzle>;

async function handleAnalysisUpdate(db: DrizzleDB, analysis: AnalysisWithRelations): Promise<Analysis> {
  return await db.transaction(async (tx) => {
    // Update or create segmentation
    let segmentationId = analysis.segmentationId;
    if (analysis.segmentation) {
      const result = await tx
        .insert(schema.segmentation)
        .values(analysis.segmentation)
        .onConflictDoUpdate({
          target: schema.segmentation.id,
          set: { imageBase64: analysis.segmentation.imageBase64 }
        })
        .returning();
      segmentationId = result[0].id;
    }

    // Update or create pith
    let pithId = analysis.pithId;
    if (analysis.pith) {
      const result = await tx
        .insert(schema.pith)
        .values(analysis.pith)
        .onConflictDoUpdate({
          target: schema.pith.id,
          set: { x: analysis.pith.x, y: analysis.pith.y }
        })
        .returning();
      pithId = result[0].id;
    }

    // Update or create rings
    let ringsId = analysis.ringsId;
    if (analysis.rings) {
      const result = await tx
        .insert(schema.rings)
        .values(analysis.rings)
        .onConflictDoUpdate({
          target: schema.rings.id,
          set: { imageBase64: analysis.rings.imageBase64 }
        })
        .returning();
      ringsId = result[0].id;
    }

    // Update or create analysis
    const result = await tx
      .insert(schema.analysis)
      .values({
        id: analysis.id,
        predictedAge: analysis.predictedAge,
        segmentationId,
        pithId,
        ringsId,
      })
      .onConflictDoUpdate({
        target: schema.analysis.id,
        set: {
          predictedAge: analysis.predictedAge,
          segmentationId,
          pithId,
          ringsId,
        }
      })
      .returning();

    return result[0];
  });
}

export function useCaptures() {
  const [captures, setCaptures] = useState<CaptureWithAnalysis[]>([]);
  const db = useSQLiteContext();
  const drizzleDb = drizzle(db, { schema });

  const loadCaptures = async () => {
    try {
      const allRows = await drizzleDb.query.capture.findMany({
        with: {
          analysis: {
            with: {
              segmentation: true,
              pith: true,
              rings: true,
            },
          },
        },
      });

      console.info('Captures length:', allRows.length);

      setCaptures(allRows as CaptureWithAnalysis[]);
    } catch (error) {
      console.error('Error loading captures:', error);
    }
  };

  const getCaptureById = async (id: string): Promise<CaptureWithAnalysis | undefined> => {
    try {
      const result = await drizzleDb.query.capture.findFirst({
        where: eq(schema.capture.id, id),
        with: {
          analysis: {
            with: {
              segmentation: true,
              pith: true,
              rings: true,
            },
          },
        },
      });

      console.info('Capture by id:', result?.id);

      return result as CaptureWithAnalysis;
    } catch (error) {
      console.error('Error getting capture by id:', error);
      return undefined;
    }
  };

  const addCapture = async (newCapture: Partial<Capture>): Promise<Capture | undefined> => {
    try {
      const captureToInsert = await createNewCapture(newCapture);
      await drizzleDb.insert(schema.capture).values(captureToInsert);

      console.info('Capture added id:', captureToInsert.id);

      await loadCaptures();
      return captureToInsert;
    } catch (error) {
      console.error('Error adding capture:', error);
      return undefined;
    }
  };

  const updateCapture = async (updatedCapture: CaptureWithAnalysis): Promise<CaptureWithAnalysis | undefined> => {
    try {
      let analysisId: number | null = updatedCapture.analysisId ?? null;

      if (updatedCapture.analysis) {
        const analysisResult = await handleAnalysisUpdate(drizzleDb, updatedCapture.analysis);
        analysisId = analysisResult.id;
      }

      await drizzleDb
        .update(schema.capture)
        .set({
          title: updatedCapture.title,
          imageBase64: updatedCapture.imageBase64,
          timestamp: updatedCapture.timestamp,
          width: updatedCapture.width,
          height: updatedCapture.height,
          analysisId: analysisId,
        })
        .where(eq(schema.capture.id, updatedCapture.id));

      console.info('Capture updated id:', updatedCapture.id);

      return await getCaptureById(updatedCapture.id);
    } catch (error) {
      console.error('Error updating capture:', error);
      return undefined;
    }
  };

  const deleteCapture = async (id: string) => {
    try {
      await drizzleDb.delete(schema.capture).where(eq(schema.capture.id, id));

      console.info('Capture deleted:', id);

      await loadCaptures();
    } catch (error) {
      console.error('Error deleting capture:', error);
    }
  };

  return {
    captures,
    loadCaptures,
    getCaptureById,
    addCapture,
    updateCapture,
    deleteCapture
  };
}