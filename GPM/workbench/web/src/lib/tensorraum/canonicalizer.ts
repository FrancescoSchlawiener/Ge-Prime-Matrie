import { request } from "../../api/request";
import { detectFileLanguage } from "./detectLanguage";
import { registerSubstrate } from "./registry";
import type {
  FileNode,
  PointerType,
  ProcessCodeOptions,
  ProcessCodeSkipReason,
  ProjectRoot,
  SequenceItem,
  SpaceNode,
  TensorraumProject,
} from "./types";

export interface ProcessCodeResult {
  fileNode: FileNode;
}

export interface ProcessCodeSkipped {
  skipped: true;
  reason: ProcessCodeSkipReason;
  languageName?: string;
}

interface ApiSequenceItem {
  t: string;
  value?: string;
  nl?: number;
  p?: string;
  closeSyntax?: string | null;
  visualStyle?: string;
  openSyntax?: string | null;
  node?: ApiTree;
}

interface ApiTree {
  sequence: ApiSequenceItem[];
  children: ApiTree[];
}

interface CanonicalizeApiResult {
  filename: string;
  language_id: string;
  normalized_code: string;
  roundtrip_ok: boolean;
  tree: ApiTree;
  registry: {
    H?: Array<{ raw: string; segments: Array<{ tag: string; value: string }> }>;
    D?: Array<{
      value: string;
      display: string;
      relation: { whole: number; den_reduced: number; ggt: number };
    }>;
  };
}

function syncRegistryMeta(root: ProjectRoot, apiRegistry: CanonicalizeApiResult["registry"]): void {
  if (!root.header.hSegments) root.header.hSegments = new Map();
  if (!root.header.dRelation) root.header.dRelation = new Map();
  for (const h of apiRegistry.H ?? []) {
    const ptr = root.header.reverseRegistry.H.get(h.raw);
    if (ptr) root.header.hSegments.set(ptr, h.segments);
  }
  for (const d of apiRegistry.D ?? []) {
    const ptr = root.header.reverseRegistry.D.get(d.value);
    if (ptr) {
      root.header.dRelation.set(ptr, {
        whole: d.relation.whole,
        den_reduced: d.relation.den_reduced,
        ggt: d.relation.ggt,
        display: d.display,
      });
    }
  }
}

function newId(prefix: string): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 11)}`;
}

function buildSpaceFromApi(root: ProjectRoot, tree: ApiTree, id: string): SpaceNode {
  const children: SpaceNode[] = [];
  const sequence: SequenceItem[] = [];
  for (const item of tree.sequence) {
    if (item.t === "CHILD" && item.node) {
      const childNode = buildSpaceFromApi(root, item.node, newId("space"));
      children.push(childNode);
      sequence.push({
        t: "CHILD",
        n: childNode,
        nl: item.nl ?? 0,
        visualStyle: item.visualStyle,
        openSyntax: item.openSyntax ?? null,
      });
    } else if (item.t === "SYS") {
      sequence.push({
        t: "SYS",
        p: item.p ?? "CLOSE_BRACKET",
        nl: item.nl ?? 0,
        closeSyntax: item.closeSyntax ?? null,
      });
    } else if (
      (item.t === "S" || item.t === "N" || item.t === "D" || item.t === "C" || item.t === "H") &&
      item.value != null
    ) {
      const kind = item.t as PointerType;
      const ptr = registerSubstrate(root, kind, item.value);
      sequence.push({ t: kind, p: ptr, nl: item.nl ?? 0 });
    }
  }
  return { id, children, sequence };
}

export async function processCode(
  project: TensorraumProject,
  code: string,
  filename: string,
  opts: ProcessCodeOptions = {},
): Promise<ProcessCodeResult | ProcessCodeSkipped | null> {
  const root = project.root;

  if (!opts.bypassFilter) {
    const detection = detectFileLanguage(filename);
    if (detection.status === "ignored") return { skipped: true, reason: "ignored" };
    if (detection.status === "unknown") return { skipped: true, reason: "unknown" };
    if (!project.activeLanguageIds.has(detection.lang.id)) {
      return { skipped: true, reason: "language_disabled", languageName: detection.lang.name };
    }
  }

  const resp = await request<{ result: CanonicalizeApiResult }>("/api/tensorraum/canonicalize", {
    method: "POST",
    body: JSON.stringify({ source: code, filename, profile: "og" }),
  });
  const data = resp.result;

  const fileId = newId("mod");
  const built = buildSpaceFromApi(root, data.tree, fileId);
  const fileNode: FileNode = {
    id: fileId,
    filename: data.filename || filename,
    languageId: data.language_id,
    rawCodeOriginal: code,
    normalizedCode: data.normalized_code,
    roundtripOk: data.roundtrip_ok,
    children: built.children,
    sequence: built.sequence,
  };
  root.children.push(fileNode);
  syncRegistryMeta(root, data.registry);

  return { fileNode };
}
