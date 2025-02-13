import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const rings = sqliteTable('rings', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  imageBase64: text('image_base64').notNull(),
});

export type Rings = typeof rings.$inferSelect;