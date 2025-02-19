import { sqliteTable, text, integer, AnySQLiteColumn } from 'drizzle-orm/sqlite-core';
import { analysis, AnalysisWithRelations } from '@/lib/database/models';
import { relations, sql } from 'drizzle-orm';
import * as Crypto from 'expo-crypto';
 
export const capture = sqliteTable('capture', {
  id: text('id').primaryKey().notNull().$defaultFn(() => Crypto.randomUUID()),
  title: text('title').notNull().$defaultFn(() => `Capture ${new Date().toLocaleString('de-DE')}`),
  imageBase64: text('image_base64').notNull(),
  createdAt: text('created_at').notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text('updated_at')
    .notNull()
    .default(sql`CURRENT_TIMESTAMP`)
    .$onUpdate(() => sql`CURRENT_TIMESTAMP`),
  width: integer('width').notNull(),
  height: integer('height').notNull(),
  analysisId: integer('analysis_id').references((): AnySQLiteColumn => analysis.id, { onDelete: 'cascade' }),
});

export const captureRelations = relations(capture, ({ one }) => ({
  analysis: one(analysis, {
    fields: [capture.analysisId],
    references: [analysis.id],
  }),
}));

export type Capture = typeof capture.$inferSelect;
export type NewCapture = typeof capture.$inferInsert;

export type CaptureWithAnalysis = Capture & {
  analysis?: AnalysisWithRelations;
};
