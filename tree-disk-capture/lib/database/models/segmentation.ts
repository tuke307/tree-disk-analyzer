import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const segmentation = sqliteTable('segmentation', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  imageBase64: text('image_base64').notNull(),
});

export type Segmentation = typeof segmentation.$inferSelect;