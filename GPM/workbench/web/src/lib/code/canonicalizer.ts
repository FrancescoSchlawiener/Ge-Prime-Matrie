import { request } from "../../api/request";
import {
  buildSpaceFromModule,
  decodeCodeModuleBase64,
  syncRegistryFromWire,
  syncRegistryMetaFromWire,
} from "../tensorraum/codeWire";
import type {
  CollisionReport,
  FileNode,
  ProcessCodeOptions,
  ProcessCodeSkipReason,
  TensorraumProject,
} from "../tensorraum/types";
import { fetchLanguageManifest, fetchLanguages, languageForExtension } from "./languages";

export interface ProcessCodeResult {
  fileNode: FileNode;
}

export interface ProcessCodeSkipped {
  skipped: true;
  reason: ProcessCodeSkipReason;
  languageName?: string;
  embeddedLanguage?: string;
}

interface CanonicalizeApiResult {
  filename: string;
  language_id: string;
  language_name?: string;
  language_manifest: { primary: string; embedded: string[]; all: string[] };
  normalized_code: string;
  reconstructed: string;
  roundtrip_ok: boolean;
  trailing_whitespace?: string;
  wire_b64: string;
  collision_report?: CollisionReport;
}

function newId(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 11)}`;
}

export async function processCode(
  project: TensorraumProject,
  code: string,
  filename: string,
  opts: ProcessCodeOptions = {},
): Promise<ProcessCodeResult | ProcessCodeSkipped | null> {
  const root = project.root;

  if (!opts.bypassFilter) {
    const langs = await fetchLanguages();
    const spec = languageForExtension(filename, langs);
    if (!spec) {
      const lower = filename.toLowerCase();
      if (langs.ignored_suffixes.some((s) => lower.endsWith(s))) {
        return { skipped: true, reason: "ignored" };
      }
      return { skipped: true, reason: "unknown" };
    }
    const manifest = await fetchLanguageManifest(code, filename);
    for (const langId of manifest.all) {
      if (!project.activeLanguageIds.has(langId)) {
        const disabled = langs.languages.find((l) => l.id === langId);
        const isEmbedded = langId !== manifest.primary;
        return {
          skipped: true,
          reason: isEmbedded ? "embedded_language_disabled" : "language_disabled",
          languageName: disabled?.name ?? langId,
          embeddedLanguage: isEmbedded ? langId : undefined,
        };
      }
    }
  }

  const resp = await request<{ result: CanonicalizeApiResult }>("/api/code/canonicalize", {
    method: "POST",
    body: JSON.stringify({ source: code, filename, profile: "og" }),
  });
  const data = resp.result;

  const { module, tables } = decodeCodeModuleBase64(data.wire_b64);
  syncRegistryFromWire(root, tables);

  const fileId = newId("mod");
  const built = buildSpaceFromModule(root, module, tables, fileId);
  const trailingWhitespace = data.trailing_whitespace ?? module.meta.trailingWhitespace ?? "";
  const fileShell: FileNode = {
    ...built,
    filename: data.filename || filename,
    languageId: data.language_id,
    rawCodeOriginal: code,
    normalizedCode: data.normalized_code,
    roundtripOk: data.roundtrip_ok,
    trailingWhitespace,
    reconstructed: data.reconstructed,
    children: built.children,
    sequence: built.sequence,
  };
  const fileNode: FileNode = { ...fileShell };

  root.children.push(fileNode);
  syncRegistryMetaFromWire(root, tables);
  if (data.collision_report) root.header.collisionReport = data.collision_report;

  return { fileNode };
}
