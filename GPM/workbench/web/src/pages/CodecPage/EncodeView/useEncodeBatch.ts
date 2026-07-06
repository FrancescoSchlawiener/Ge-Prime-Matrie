import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../../api/client";
import { fetchSizeEncodeBatch, fetchSizeEncodeWord, useSizeCompare } from "../../../components/result";
import { saveDecodeDraft } from "../../../utils/sessionBridge";
import type { EncodeWordResult, WordSizeState } from "./encodeTypes";

export function useEncodeBatch() {
  const navigate = useNavigate();
  const [text, setText] = useState("HALLO WELT");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [words, setWords] = useState<EncodeWordResult[]>([]);
  const [failed, setFailed] = useState<string[]>([]);
  const [skipped, setSkipped] = useState(0);
  const [truncated, setTruncated] = useState(false);
  const [maxWords, setMaxWords] = useState(50);
  const [profile] = useState("og");
  const [wordSizes, setWordSizes] = useState<Record<number, WordSizeState>>({});
  const batchSize = useSizeCompare();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setWords([]);
    setFailed([]);
    batchSize.reset();
    setWordSizes({});
    try {
      const resp = await api.encodeBatch(text, profile, true);
      const r = resp.result as {
        words?: EncodeWordResult[];
        failed?: string[];
        skipped?: number;
        truncated?: boolean;
        max_words?: number;
      };
      setWords(r.words ?? []);
      setFailed(r.failed ?? []);
      setSkipped(r.skipped ?? 0);
      setTruncated(Boolean(r.truncated));
      setMaxWords(r.max_words ?? 50);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  function copyToDecode(substance: number, index: number) {
    saveDecodeDraft(substance, index);
    navigate("/codec/decodieren");
  }

  async function runBatchSizeCompare() {
    const hashes = words.map((w) => w.content_hash).filter(Boolean);
    if (!hashes.length) return;
    await batchSize.run(() => fetchSizeEncodeBatch(hashes, profile));
  }

  async function runWordSizeCompare(index: number, row: EncodeWordResult) {
    setWordSizes((prev) => ({ ...prev, [index]: { data: null, loading: true, error: null } }));
    try {
      const data = await fetchSizeEncodeWord(row.content_hash, profile, {
        original: row.word,
        normalized: row.normalized,
        substance: row.substance,
        perm_index: row.index,
      });
      setWordSizes((prev) => ({ ...prev, [index]: { data, loading: false, error: null } }));
    } catch (err) {
      setWordSizes((prev) => ({
        ...prev,
        [index]: {
          data: null,
          loading: false,
          error: err instanceof Error ? err.message : String(err),
        },
      }));
    }
  }

  return {
    text,
    setText,
    loading,
    error,
    words,
    failed,
    skipped,
    truncated,
    maxWords,
    wordSizes,
    batchSize,
    submit,
    copyToDecode,
    runBatchSizeCompare,
    runWordSizeCompare,
    hasResults: words.length > 0 || failed.length > 0,
  };
}
