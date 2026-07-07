export type PointerType = "S" | "N" | "D" | "C" | "H";

export type BlockStyle = "brace" | "indent" | "keyword" | "tag" | "flat";
export type CommentStyle = "c" | "hash" | "sql" | "none";

export interface BlockPair {
  open: string;
  close: string;
}

export interface LanguageConfig {
  id: string;
  name: string;
  ext: string[];
  blockStyle: BlockStyle;
  commentStyle: CommentStyle;
  blockPairs?: BlockPair[];
}

export interface SequenceChildItem {
  t: "CHILD";
  n: SpaceNode;
  nl: number;
  colPrefix?: string;
  visualStyle?: string;
  openSyntax?: string | null;
}

export interface SequencePointerItem {
  t: PointerType;
  p: string;
  nl: number;
  colPrefix?: string;
  bigint?: boolean;
}

export interface SequenceSysItem {
  t: "SYS";
  p: string;
  nl: number;
  colPrefix?: string;
  closeSyntax?: string | null;
}

export type SequenceItem = SequenceChildItem | SequencePointerItem | SequenceSysItem;

export interface SpaceNode {
  id: string;
  children: SpaceNode[];
  sequence: SequenceItem[];
  visualStyle?: string;
  openSyntax?: string;
}

export interface FileNode extends SpaceNode {
  filename: string;
  languageId: string;
  rawCodeOriginal: string;
  normalizedCode: string;
  roundtripOk?: boolean;
  trailingWhitespace?: string;
  reconstructed?: string;
}

export interface RegistryMaps {
  S: Map<string, string>;
  N: Map<string, string>;
  D: Map<string, string>;
  C: Map<string, string>;
  H: Map<string, string>;
}

export interface ProjectRoot {
  id: string;
  name: string;
  children: FileNode[];
  header: {
    registry: RegistryMaps;
    reverseRegistry: RegistryMaps;
    hSegments?: Map<string, Array<{ tag: string; value: string }>>;
    dRelation?: Map<string, { whole: number; den_reduced: number; ggt: number; display: string }>;
    sSubstance?: Map<string, { substance: string; permIndex: string }>;
    cSubstance?: Map<string, { substance: string; permIndex: string }>;
    hSubstance?: Map<string, { substance: string }>;
    collisionReport?: CollisionReport;
  };
}

export interface CollisionCategory {
  entries: number;
  identities: number;
  collisions: number;
  collision_free: boolean;
}

export type CollisionReport = Partial<Record<PointerType, CollisionCategory>>;

export interface TensorraumProject {
  id: string;
  name: string;
  root: ProjectRoot;
  activeLanguageIds: Set<string>;
  crossLanguageAnalysis: boolean;
  structuralOnly: boolean;
  sourceSaveId?: string;
}

export interface ProcessCodeOptions {
  bypassFilter?: boolean;
}

export type ProcessCodeSkipReason = "ignored" | "unknown" | "language_disabled" | "embedded_language_disabled";

export interface TokenBlock {
  block: "open" | "close";
  nl: number;
  bracket?: string;
  keyword?: string;
  expectedCloser?: string;
  tag?: string;
}

export interface TokenValue {
  type: PointerType;
  value: string;
  nl: number;
}

export type NormalizedToken = TokenBlock | TokenValue;

export interface ProjectStats {
  files: number;
  spaces: number;
  pointers: number;
  activeLanguages: number;
  totalLanguages: number;
}

export type RegistrySubview = "registry" | "tree";

export type TensorraumView =
  | "workspace"
  | "registry"
  | "redundancy"
  | "reversibility"
  | "storage";

export type RedundancySubview = "block" | "sentence";

export interface LogEntry {
  id: string;
  message: string;
  at: number;
}
