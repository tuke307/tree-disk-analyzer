import * as SQLite from 'expo-sqlite';

export class TreeDiskDatabase {
  public db: SQLite.SQLiteDatabase

  private constructor(db: SQLite.SQLiteDatabase) {
    this.db = db;
  }

  public static async createInstance(): Promise<TreeDiskDatabase> {
    const db = await SQLite.openDatabaseAsync('treeDiskDB');
    return new TreeDiskDatabase(db);
  }
}

export const db = TreeDiskDatabase.createInstance();