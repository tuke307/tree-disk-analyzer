import { sql } from 'drizzle-orm';
import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';

export const pith = sqliteTable('pith', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  x: integer('x').notNull(),
  y: integer('y').notNull(),
  createdAt: text('created_at').notNull().default(sql`CURRENT_TIMESTAMP`),
  updatedAt: text('updated_at')
    .notNull()
    .default(sql`CURRENT_TIMESTAMP`)
    .$onUpdate(() => sql`CURRENT_TIMESTAMP`),
});

export type Pith = typeof pith.$inferSelect;
export type NewPith = typeof pith.$inferInsert;
