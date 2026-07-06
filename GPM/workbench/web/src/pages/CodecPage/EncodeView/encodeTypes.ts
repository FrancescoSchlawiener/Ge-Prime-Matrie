import type { Step } from "../../../api/gpm-api";
import type { SizeComparisonData } from "../../../components/result";

export interface EncodeWordResult {
  word: string;
  normalized: string;
  substance: number;
  index: number;
  content_hash: string;
  steps?: Step[];
}

export interface WordSizeState {
  data: SizeComparisonData | null;
  loading: boolean;
  error: string | null;
}

export const EMPTY_WORD_SIZE: WordSizeState = { data: null, loading: false, error: null };
