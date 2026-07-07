import { getLanguagesCache, languageSpecToConfig } from "../code/languages";
import { SUPPORTED_LANGUAGES } from "./constants";
import type {
  FileNode,
  LanguageConfig,
  PointerType,
  RegistryMaps,
  SequenceItem,
  SequenceSysItem,
  SpaceNode,
} from "./types";

export const INDENT_UNIT = "    ";
export const REVERSIBILITY_CARD_LIMIT = 15;

export interface FlatToken {
  block?: "open" | "close";
  type?: PointerType;
  value?: string;
  nl: number;
}

export interface ReversibilityVerdict {
  ok: boolean;
  reason?: string;
  mismatchIndex?: number;
}

export interface FileReversibilityResult {
  file: FileNode;
  decompiled: string;
  verdict: ReversibilityVerdict;
  originalLineCount: number;
  decompiledLineCount: number;
  tokenCount: number;
  maxDepth: number;
}

export function resolveLanguageConfig(languageId: string): LanguageConfig {
  const payload = getLanguagesCache();
  if (payload) {
    const spec = payload.languages.find((l) => l.id === languageId);
    if (spec) return languageSpecToConfig(spec);
  }
  return SUPPORTED_LANGUAGES.find((l) => l.id === languageId) ?? SUPPORTED_LANGUAGES[0];
}

function gapPrefix(
  nl: number,
  colPrefix: string | undefined,
  depth: number,
  visualStyle: string | undefined,
): string {
  let out = "\n".repeat(nl);
  if (colPrefix) {
    out += colPrefix;
  } else if (visualStyle === "indent" && nl > 0) {
    out += INDENT_UNIT.repeat(depth);
  }
  return out;
}

function childBlockPrefix(nl: number, colPrefix: string | undefined): string {
  if (!nl && !colPrefix) return "";
  return "\n".repeat(nl) + (colPrefix ?? "");
}

export function reconstruct(node: SpaceNode, registry: RegistryMaps, depth = 0): string {
  const visual = node.visualStyle;
  let codeOut = "";
  for (const item of node.sequence) {
    if (item.t === "CHILD") {
      const isIndentStyle = item.visualStyle === "indent";
      const childDepth = isIndentStyle ? depth + 1 : depth;
      codeOut += childBlockPrefix(item.nl || 0, item.colPrefix);
      codeOut += reconstruct(item.n, registry, childDepth);
    } else if (item.t === "SYS" && item.p === "CLOSE_BRACKET") {
      const closeTxt = item.closeSyntax ?? "";
      codeOut += gapPrefix(item.nl || 0, item.colPrefix, depth, visual) + closeTxt;
    } else if (item.t === "S" || item.t === "N" || item.t === "D" || item.t === "C" || item.t === "H") {
      const realValue = registry[item.t].get(item.p);
      let text = realValue ?? item.p;
      if (item.t === "N" && item.bigint) text += "n";
      codeOut += gapPrefix(item.nl || 0, item.colPrefix, depth, visual) + text;
    }
  }
  return codeOut;
}

export function reconstructFile(file: FileNode, registry: RegistryMaps): string {
  const body = reconstruct(file, registry);
  return body + (file.trailingWhitespace ?? "");
}

export function reconstructFlat(items: SequenceItem[], registry: RegistryMaps): string {
  let codeOut = "";
  let depth = 0;
  for (const item of items) {
    if (item.t === "CHILD") {
      codeOut += childBlockPrefix(item.nl || 0, item.colPrefix);
      depth++;
    } else if (item.t === "SYS" && item.p === "BLOCK_OPEN") {
      const blockOpen = item as SequenceSysItem & { visualStyle?: string; openSyntax?: string | null };
      const isIndentStyle = blockOpen.visualStyle === "indent";
      const openTxt = blockOpen.openSyntax ?? "";
      codeOut += gapPrefix(item.nl || 0, item.colPrefix, isIndentStyle ? depth + 1 : depth, blockOpen.visualStyle) + openTxt;
      depth++;
    } else if (item.t === "SYS" && item.p === "CLOSE_BRACKET") {
      depth = Math.max(0, depth - 1);
      const closeTxt = item.closeSyntax ?? "";
      codeOut += gapPrefix(item.nl || 0, item.colPrefix, depth, undefined) + closeTxt;
    } else if (item.t === "S" || item.t === "N" || item.t === "D" || item.t === "C" || item.t === "H") {
      const realValue = registry[item.t].get(item.p);
      if (realValue === undefined) continue;
      codeOut += gapPrefix(item.nl || 0, item.colPrefix, depth, undefined) + realValue;
    }
  }
  return codeOut;
}

function flattenForVerify(node: SpaceNode, registry: RegistryMaps, out: FlatToken[] = []): FlatToken[] {
  for (const item of node.sequence) {
    if (item.t === "CHILD") {
      out.push({ block: "open", nl: item.nl || 0 });
      flattenForVerify(item.n, registry, out);
    } else if (item.t === "SYS" && item.p === "CLOSE_BRACKET") {
      out.push({ block: "close", nl: item.nl || 0 });
    } else if (item.t === "S" || item.t === "N" || item.t === "D" || item.t === "C" || item.t === "H") {
      out.push({
        type: item.t,
        value: registry[item.t].get(item.p),
        nl: item.nl || 0,
      });
    }
  }
  return out;
}

export function verifyReversibility(
  file: FileNode,
  registry: RegistryMaps,
  decompiledText?: string,
): ReversibilityVerdict {
  const decompiled = decompiledText ?? file.reconstructed ?? reconstructFile(file, registry);
  const byteMatch = decompiled === file.normalizedCode;

  if (typeof file.roundtripOk === "boolean") {
    if (file.roundtripOk && byteMatch) return { ok: true };
    if (!file.roundtripOk) {
      return {
        ok: false,
        reason: byteMatch
          ? "API-Round-Trip fehlgeschlagen (roundtrip_ok=false)"
          : "API-Round-Trip fehlgeschlagen; Dekompiliert weicht von normalisiertem Code ab",
      };
    }
    return { ok: false, reason: "Dekompiliert weicht von normalisiertem Code ab" };
  }

  return byteMatch
    ? { ok: true }
    : { ok: false, reason: "Dekompiliert weicht von normalisiertem Code ab" };
}

export function measureMaxDepth(node: SpaceNode, currentDepth = 0): number {
  let max = currentDepth;
  for (const child of node.children ?? []) {
    const childMax = measureMaxDepth(child, currentDepth + 1);
    if (childMax > max) max = childMax;
  }
  return max;
}

export function countLines(code: string): number {
  if (!code) return 0;
  return code.split("\n").length;
}

export function formatCodeWithLineNumbers(code: string): string {
  const lines = code.split("\n");
  const width = Math.max(2, String(lines.length).length);
  return lines.map((line, i) => `${String(i + 1).padStart(width, " ")}  ${line}`).join("\n");
}

export function verifyFileReversibility(file: FileNode, registry: RegistryMaps): FileReversibilityResult {
  const decompiled = file.reconstructed ?? reconstructFile(file, registry);
  const verdict = verifyReversibility(file, registry, decompiled);
  const originalFlat = flattenForVerify(file, registry);

  return {
    file,
    decompiled,
    verdict,
    originalLineCount: countLines(file.normalizedCode),
    decompiledLineCount: countLines(decompiled),
    tokenCount: originalFlat.length,
    maxDepth: measureMaxDepth(file),
  };
}

export function verifyProjectReversibility(
  files: FileNode[],
  registry: RegistryMaps,
): FileReversibilityResult[] {
  return files.map((file) => verifyFileReversibility(file, registry));
}
