/** Minimal API types — replace via `npm run codegen` when API is running. */

export interface Step {
  id: string;
  title: string;
  detail: string;
  lines?: string[];
  values?: Record<string, string | number | boolean>;
  formula?: string | null;
  extra?: string | null;
}

export interface CurveMeta {
  full_count: number;
  downsampled: boolean;
  limit: number;
}

export interface WorkbenchResponse<T = Record<string, unknown>> {
  result: T;
  steps: Step[];
  explain_links?: string[];
  warnings?: string[];
  curve_meta?: CurveMeta | null;
}

export interface ProfileItem {
  id: string;
  label: string;
}

export interface CompileResult {
  document_ref: string;
  content_hash?: string;
  mode: string;
  profile: string;
  roundtrip_ok?: boolean;
  roundtrip_details?: { nl_ok?: boolean; hybrid_ok?: boolean; byte_identical?: boolean };
  registry_entries?: Array<Record<string, unknown>>;
  fence_boundaries?: Array<Record<string, unknown>>;
  gaps?: string[];
  tokens?: Array<{ word_id: number; surface?: string }>;
  cells?: Array<{
    cell_index: number;
    token_start: number;
    token_count: number;
    ggt?: number;
    ggt_kgv_ratio?: number;
    category_count?: number;
  }>;
  cell_count?: number;
  token_count?: number;
}
