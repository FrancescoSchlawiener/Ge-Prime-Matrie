import { useCallback, useEffect, useState } from "react";
import { api } from "../../api/client";

export interface LangRow {
  language: string;
  count: number;
}

export function useDatenbankStats() {
  const [rows, setRows] = useState<LangRow[]>([]);
  const [total, setTotal] = useState(0);
  const [connected, setConnected] = useState(false);
  const [dbName, setDbName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.dbStats();
      setTotal(data.total);
      setRows(data.by_language ?? []);
      setConnected(data.connected);
      setDbName(data.db_name ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { rows, total, connected, dbName, loading, error, load };
}
