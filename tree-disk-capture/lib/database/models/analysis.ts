import { sqliteTable, integer } from 'drizzle-orm/sqlite-core';
import { segmentation, pith, rings, Segmentation, Pith, Rings } from '@/lib/database/models';
import { relations } from 'drizzle-orm';

export const analysis = sqliteTable('analysis', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  predictedAge: integer('predicted_age'),
  segmentationId: integer('segmentation_id').references(() => segmentation.id, { onDelete: 'cascade' }),
  pithId: integer('pith_id').references(() => pith.id, { onDelete: 'cascade' }),
  ringsId: integer('rings_id').references(() => rings.id, { onDelete: 'cascade' }),
});

export const analysisRelations = relations(analysis, ({ one }) => ({
  segmentation: one(segmentation, {
    fields: [analysis.segmentationId],
    references: [segmentation.id],
  }),
  pith: one(pith, {
    fields: [analysis.pithId],
    references: [pith.id],
  }),
  rings: one(rings, {
    fields: [analysis.ringsId],
    references: [rings.id],
  }),
}));

export type Analysis = typeof analysis.$inferSelect;

export type AnalysisWithRelations = Analysis & {
  segmentation?: Segmentation;
  pith?: Pith;
  rings?: Rings;
};