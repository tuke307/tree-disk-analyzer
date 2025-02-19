import { sqliteTable, integer, text, AnySQLiteColumn } from 'drizzle-orm/sqlite-core';
import { segmentation, pith, rings, Segmentation, Pith, Rings } from '@/lib/database/models';
import { relations, sql } from 'drizzle-orm';

export const analysis = sqliteTable('analysis', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  predictedAge: integer('predicted_age'),
  segmentationId: integer('segmentation_id').references((): AnySQLiteColumn => segmentation.id, { onDelete: 'cascade' }),
  pithId: integer('pith_id').references((): AnySQLiteColumn => pith.id, { onDelete: 'cascade' }),
  ringsId: integer('rings_id').references((): AnySQLiteColumn => rings.id, { onDelete: 'cascade' }),
  createdAt: text('created_at').notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text('updated_at')
    .notNull()
    .default(sql`CURRENT_TIMESTAMP`)
    .$onUpdate(() => sql`CURRENT_TIMESTAMP`),
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
export type NewAnalysis = typeof analysis.$inferInsert;

export type AnalysisWithRelations = Analysis & {
  segmentation?: Segmentation;
  pith?: Pith;
  rings?: Rings;
};