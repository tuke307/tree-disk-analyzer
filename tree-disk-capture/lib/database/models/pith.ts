import { sqliteTable, integer } from 'drizzle-orm/sqlite-core';

export const pith = sqliteTable('pith', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  x: integer('x').notNull(),
  y: integer('y').notNull(),
});

export type Pith = typeof pith.$inferSelect;