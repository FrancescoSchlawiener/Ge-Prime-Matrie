export interface WorkbenchErrorBody {
  error?: { code: string; message: string };
  detail?: string | { code?: string; message?: string };
}

export class WorkbenchError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

export interface JobRecord {
  job_id: string;
  kind: string;
  status: "pending" | "running" | "done" | "failed";
  progress: { phase: string; percent: number; message: string; elapsed_ms: number };
  result: Record<string, unknown> | null;
  error: string | null;
}

function parseError(err: WorkbenchErrorBody): WorkbenchError {
  if (err.error?.code) {
    return new WorkbenchError(err.error.code, err.error.message);
  }
  if (typeof err.detail === "object" && err.detail?.code) {
    return new WorkbenchError(err.detail.code, err.detail.message ?? err.detail.code);
  }
  const msg = typeof err.detail === "string" ? err.detail : JSON.stringify(err);
  return new WorkbenchError("http_error", msg);
}

const BASE = "";

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({ detail: res.statusText }))) as WorkbenchErrorBody;
    throw parseError(err);
  }
  return res.json() as Promise<T>;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function pollJob(jobId: string, onProgress?: (rec: JobRecord) => void): Promise<JobRecord> {
  let backoff = 400;
  for (;;) {
    try {
      const rec = await request<JobRecord>(`/api/jobs/${jobId}`);
      onProgress?.(rec);
      if (rec.status === "done" || rec.status === "failed") return rec;
      backoff = 400;
      await sleep(400);
    } catch (e) {
      await sleep(backoff);
      backoff = Math.min(backoff * 2, 4000);
      if (backoff >= 4000) throw e;
    }
  }
}

export interface RedundancyScanOptions {
  canonical?: boolean;
  window_mode?: "fixed" | "adaptive";
  window_min?: number;
  window_max?: number;
  window_size?: number;
  structural_only?: boolean;
  level?: "token" | "block";
}
