import { request } from "../request";

export const systemEndpoints = {
  health: () => request<{ status: string }>("/api/health"),
  version: () => request<{ workbench: string }>("/api/version"),
  profiles: () => request<{ profiles: { id: string; label: string }[] }>("/api/profiles"),
  dbStats: () =>
    request<{
      total: number;
      by_language: { language: string; count: number }[];
      db_name: string;
      connected: boolean;
    }>("/api/db/stats"),
};
