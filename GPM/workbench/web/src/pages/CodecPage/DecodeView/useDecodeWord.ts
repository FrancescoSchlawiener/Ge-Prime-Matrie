import { useState } from "react";
import { api } from "../../../api/client";
import type { Step } from "../../../api/gpm-api";
import { fetchSizeDecodeWord, useSizeCompare } from "../../../components/result";
import { loadDecodeDraft } from "../../../utils/sessionBridge";
import type { DecodeResultData } from "./decodeSummary";

export function useDecodeWord() {
  const draft = loadDecodeDraft();
  const [substance, setSubstance] = useState(draft?.substance ?? "");
  const [index, setIndex] = useState(draft?.index ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DecodeResultData | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [profile] = useState("og");
  const sizeCompare = useSizeCompare();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    sizeCompare.reset();
    try {
      const resp = await api.decodeWord(Number(substance), Number(index), profile, true);
      const r = resp.result as {
        word?: string;
        normalized?: string;
        substance?: number;
        index?: number;
        ingredients?: Record<string, number>;
        content_hash?: string;
      };
      setResult({
        word: r.normalized ?? r.word ?? "—",
        substance: Number(r.substance),
        index: Number(r.index),
        content_hash: r.content_hash ?? "",
        ingredients: r.ingredients,
      });
      setSteps(resp.steps);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function runSizeCompare() {
    if (!result?.content_hash) return;
    await sizeCompare.run(() =>
      fetchSizeDecodeWord(result.content_hash, profile, {
        substance: result.substance,
        perm_index: result.index,
      }),
    );
  }

  return {
    substance,
    setSubstance,
    index,
    setIndex,
    loading,
    error,
    result,
    steps,
    sizeCompare,
    submit,
    runSizeCompare,
  };
}
