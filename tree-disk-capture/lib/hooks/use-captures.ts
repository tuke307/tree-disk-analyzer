import { useState, useEffect } from 'react';
import { db } from '@/lib/database/db';
import { Capture } from '@/lib/database/models';

export function useCaptures() {
  const [captures, setCaptures] = useState<Capture[]>([]);
  const [database, setDatabase] = useState<any>(null);

  useEffect(() => {
    const initDb = async () => {
      try {
        // Wait for the TreeDiskDatabase instance and get its db property
        const treeDiskInstance = await db;
        const sqldb = treeDiskInstance.db;
        // Create the captures table if it does not exist.
        await sqldb.execAsync(`
          PRAGMA journal_mode = WAL;
          CREATE TABLE IF NOT EXISTS captures (
            id TEXT PRIMARY KEY NOT NULL,
            data TEXT NOT NULL
          );
        `);
        setDatabase(sqldb);
        loadCaptures(sqldb);
      } catch (error) {
        console.error('Error initializing database:', error);
      }
    };

    initDb();
  }, []);

  const loadCaptures = async (sqldb: any = database) => {
    if (!sqldb) return;
    try {
      const allRows = await sqldb.getAllAsync('SELECT * FROM captures');
      // Parse the JSON stored in the data column
      const parsedCaptures = allRows.map((row: any) => ({
        id: row.id,
        ...JSON.parse(row.data)
      }));
      setCaptures(parsedCaptures);
    } catch (error) {
      console.error('Error loading captures:', error);
    }
  };

  const getCaptureById = async (id: string): Promise<Capture | undefined> => {
    if (!database) return undefined;
    try {
      const row = await database.getFirstAsync('SELECT * FROM captures WHERE id = ?', id);
      return row ? { id: row.id, ...JSON.parse(row.data) } : undefined;
    } catch (error) {
      console.error('Error getting capture by id:', error);
      return undefined;
    }
  };

  const addCapture = async (capture: Capture) => {
    if (!database) return;
    try {
      const data = JSON.stringify(capture);
      await database.runAsync(
        'INSERT INTO captures (id, data) VALUES (?, ?)',
        String(capture.id),
        data
      );
      loadCaptures();
    } catch (error) {
      console.error('Error adding capture:', error);
    }
  };

  const updateCapture = async (capture: Capture) => {
    if (!database) return;
    try {
      const data = JSON.stringify(capture);
      await database.runAsync(
        'UPDATE captures SET data = ? WHERE id = ?',
        data,
        String(capture.id)
      );
      loadCaptures();
    } catch (error) {
      console.error('Error updating capture:', error);
    }
  };

  const deleteCapture = async (id: string) => {
    if (!database) return;
    try {
      await database.runAsync('DELETE FROM captures WHERE id = ?', id);
      loadCaptures();
    } catch (error) {
      console.error('Error deleting capture:', error);
    }
  };

  return { captures, loadCaptures, getCaptureById, addCapture, updateCapture, deleteCapture };
}