import type { GpmProjectSave, StorageIndexEntry } from "./persistence";
import { storageIndexEntry, validateSave } from "./persistence";

const INDEX_KEY = "gpm.tensorraum.saves.index.v1";
const PAYLOAD_PREFIX = "gpm.tensorraum.save.v1.";

export type StorageErrorCode = "QUOTA_EXCEEDED" | "NOT_FOUND" | "PARSE_ERROR";

export class StorageError extends Error {
  constructor(
    public code: StorageErrorCode,
    message?: string,
  ) {
    super(message ?? code);
    this.name = "StorageError";
  }
}

function readIndex(): StorageIndexEntry[] {
  if (typeof localStorage === "undefined") return [];
  try {
    const raw = localStorage.getItem(INDEX_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (e): e is StorageIndexEntry =>
        !!e &&
        typeof e === "object" &&
        typeof (e as StorageIndexEntry).saveId === "string",
    );
  } catch {
    return [];
  }
}

function writeIndex(entries: StorageIndexEntry[]): void {
  if (typeof localStorage === "undefined") return;
  try {
    localStorage.setItem(INDEX_KEY, JSON.stringify(entries));
  } catch (err) {
    if (isQuotaError(err)) throw new StorageError("QUOTA_EXCEEDED");
    throw err;
  }
}

function isQuotaError(err: unknown): boolean {
  if (!err || typeof err !== "object") return false;
  const e = err as { name?: string; code?: number };
  return e.name === "QuotaExceededError" || e.code === 22;
}

export function listSaves(): StorageIndexEntry[] {
  return readIndex().sort((a, b) => b.savedAt.localeCompare(a.savedAt));
}

export function getSave(saveId: string): GpmProjectSave | null {
  if (typeof localStorage === "undefined") return null;
  try {
    const raw = localStorage.getItem(`${PAYLOAD_PREFIX}${saveId}`);
    if (!raw) return null;
    const data = JSON.parse(raw) as unknown;
    if (!validateSave(data)) return null;
    return data;
  } catch {
    return null;
  }
}

export function putSave(save: GpmProjectSave): void {
  if (typeof localStorage === "undefined") return;
  const entry = storageIndexEntry(save);
  try {
    localStorage.setItem(`${PAYLOAD_PREFIX}${save.saveId}`, JSON.stringify(save));
    const index = readIndex().filter((e) => e.saveId !== save.saveId);
    index.push(entry);
    writeIndex(index);
  } catch (err) {
    if (isQuotaError(err)) throw new StorageError("QUOTA_EXCEEDED");
    throw err;
  }
}

export function deleteSave(saveId: string): void {
  if (typeof localStorage === "undefined") return;
  localStorage.removeItem(`${PAYLOAD_PREFIX}${saveId}`);
  writeIndex(readIndex().filter((e) => e.saveId !== saveId));
}

export function importSaveToStorage(save: GpmProjectSave): void {
  putSave(save);
}
