import { sql } from 'drizzle-orm';
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const rings = sqliteTable('rings', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  imageBase64: text('image_base64').notNull(),
  createdAt: text('created_at').notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text('updated_at')
    .notNull()
    .default(sql`CURRENT_TIMESTAMP`)
    .$onUpdate(() => sql`CURRENT_TIMESTAMP`),
});

export type Rings = typeof rings.$inferSelect;
export type NewRings = typeof rings.$inferInsert;
