import { useState, useEffect } from 'react';
import * as schema from '@/lib/database/models';
import { drizzle } from 'drizzle-orm/expo-sqlite';
import { useSQLiteContext } from 'expo-sqlite';
import { eq } from 'drizzle-orm';


type DrizzleDB = ReturnType<typeof drizzle>;

async function handleAnalysisUpdate(db: DrizzleDB, analysis: schema.AnalysisWithRelations): Promise<schema.Analysis> {
  return await db.transaction(async (tx) => {
    // Handle segmentation
    let segmentationId = analysis.segmentationId;
    if (analysis.segmentation) {
      if (segmentationId) {
        // Update existing segmentation
        await tx
          .update(schema.segmentation)
          .set({ imageBase64: analysis.segmentation.imageBase64 })
          .where(eq(schema.segmentation.id, segmentationId));
      } else {
        // Create new segmentation
        const result = await tx
          .insert(schema.segmentation)
          .values({ imageBase64: analysis.segmentation.imageBase64 })
          .returning();
        segmentationId = result[0].id;
      }
    }

    // Handle pith
    let pithId = analysis.pithId;
    if (analysis.pith) {
      if (pithId) {
        // Update existing pith
        await tx
          .update(schema.pith)
          .set({ x: analysis.pith.x, y: analysis.pith.y })
          .where(eq(schema.pith.id, pithId));
      } else {
        // Create new pith
        const result = await tx
          .insert(schema.pith)
          .values({ x: analysis.pith.x, y: analysis.pith.y })
          .returning();
        pithId = result[0].id;
      }
    }

    // Handle rings
    let ringsId = analysis.ringsId;
    if (analysis.rings) {
      if (ringsId) {
        // Update existing rings
        await tx
          .update(schema.rings)
          .set({ imageBase64: analysis.rings.imageBase64 })
          .where(eq(schema.rings.id, ringsId));
      } else {
        // Create new rings
        const result = await tx
          .insert(schema.rings)
          .values({ imageBase64: analysis.rings.imageBase64 })
          .returning();
        ringsId = result[0].id;
      }
    }

    // Handle analysis
    if (analysis.id) {
      // Update existing analysis
      const result = await tx
        .update(schema.analysis)
        .set({
          predictedAge: analysis.predictedAge,
          segmentationId,
          pithId,
          ringsId,
        })
        .where(eq(schema.analysis.id, analysis.id))
        .returning();
      return result[0];
    } else {
      // Create new analysis
      const result = await tx
        .insert(schema.analysis)
        .values({
          predictedAge: analysis.predictedAge,
          segmentationId,
          pithId,
          ringsId,
        })
        .returning();
      return result[0];
    }
  });
}

export function useCaptures() {
  const [captures, setCaptures] = useState<schema.CaptureWithAnalysis[]>([]);
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

      setCaptures(allRows as schema.CaptureWithAnalysis[]);
    } catch (error) {
      console.error('Error loading captures:', error);
    }
  };

  const getCaptureById = async (id: string): Promise<schema.CaptureWithAnalysis | undefined> => {
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

      return result as schema.CaptureWithAnalysis;
    } catch (error) {
      console.error('Error getting capture by id:', error);
      return undefined;
    }
  };

  const addCapture = async (newCapture: schema.NewCapture): Promise<schema.Capture | undefined> => {
    try {
      const insertedCaptures = await drizzleDb.insert(schema.capture).values({...newCapture}).returning();

      const insertedCapture = insertedCaptures[0];

      console.info('Capture added id:', insertedCapture.id);

      await loadCaptures();
      return insertedCapture;
    } catch (error) {
      console.error('Error adding capture:', error);
      return undefined;
    }
  };

  const updateCapture = async (updatedCapture: schema.CaptureWithAnalysis): Promise<schema.CaptureWithAnalysis | undefined> => {
    try {
      console.info('Updated capture:', updatedCapture.id);
      
      if (updatedCapture.analysis) {
        const analysisResult = await handleAnalysisUpdate(drizzleDb, updatedCapture.analysis);
        
        await drizzleDb
          .update(schema.capture)
          .set({
            title: updatedCapture.title,
            imageBase64: updatedCapture.imageBase64,
            width: updatedCapture.width,
            height: updatedCapture.height,
            analysisId: analysisResult.id,
          })
          .where(eq(schema.capture.id, updatedCapture.id));
      } else {
        await drizzleDb
          .update(schema.capture)
          .set({
            title: updatedCapture.title,
            imageBase64: updatedCapture.imageBase64,
            width: updatedCapture.width,
            height: updatedCapture.height,
          })
          .where(eq(schema.capture.id, updatedCapture.id));
      }

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