import type { Config } from 'drizzle-kit';

export default {
  schema: './lib/database/models',
  out: './drizzle',
  dialect: 'sqlite',
  driver: 'expo',
  verbose: true,
  strict: true,
} satisfies Config;