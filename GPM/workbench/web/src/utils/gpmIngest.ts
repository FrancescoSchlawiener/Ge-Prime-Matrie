import { api } from "../api/client";

const GPM_VERSIONS = new Set([4, 8, 9, 10]);
const GPC_MAGIC = [0x47, 0x50, 0x43, 0x01] as const;

export type GpmIngestResult =
  | { kind: "gpm"; result: Record<string, unknown> }
  | { kind: "text"; text: string };

export function isGpmOrGpcMagic(head: Uint8Array): boolean {
  if (head.length < 4) return false;
  if (head[0] === 0x47 && head[1] === 0x50 && head[2] === 0x43 && head[3] === GPC_MAGIC[3]) {
    return true;
  }
  if (head[0] === 0x47 && head[1] === 0x50 && head[2] === 0x4d && GPM_VERSIONS.has(head[3])) {
    return true;
  }
  return false;
}

async function readFileHead(file: File, length = 4): Promise<Uint8Array> {
  const slice = file.slice(0, length);
  const buffer = await slice.arrayBuffer();
  return new Uint8Array(buffer);
}

export function basenameWithoutExtension(name: string): string {
  const base = name.replace(/^.*[/\\]/, "");
  return base.replace(/\.(gpm|gpc)$/i, "").replace(/\.[^.]+$/, "") || "document";
}

export async function ingestGpmOrTextFile(file: File, key?: string): Promise<GpmIngestResult> {
  const head = await readFileHead(file);
  if (isGpmOrGpcMagic(head)) {
    const resp = await api.gpmReadFile(file, key);
    return { kind: "gpm", result: resp.result as Record<string, unknown> };
  }
  const text = await file.text();
  return { kind: "text", text };
}

export async function loadGpmOrText(file: File): Promise<string> {
  const ingested = await ingestGpmOrTextFile(file);
  if (ingested.kind === "text") return ingested.text;
  return String(ingested.result.reconstructed_text ?? "");
}
