import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
import { analysis, AnalysisWithRelations } from '@/lib/database/models';
import { relations } from 'drizzle-orm';

export const capture = sqliteTable('capture', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  imageBase64: text('image_base64').notNull(),
  timestamp: text('timestamp').notNull(),
  width: integer('width').notNull(),
  height: integer('height').notNull(),
  analysisId: integer('analysis_id').references(() => analysis.id, { onDelete: 'cascade' }),
});

export const captureRelations = relations(capture, ({ one }) => ({
  analysis: one(analysis, {
    fields: [capture.analysisId],
    references: [analysis.id],
  }),
}));

export type Capture = typeof capture.$inferSelect;

export type CaptureWithAnalysis = typeof capture.$inferSelect & {
  analysis?: AnalysisWithRelations;
};
