import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../../../api/client";
import type { Step } from "../../../api/gpm-api";
import { fetchSizeEncodeBatch, useSizeCompare } from "../../../components/result";
import { loadWordPairDraft } from "../../../utils/sessionBridge";
import { mapApiError, parseMode, type PairMode } from "./wortpaarMode";

export function useWortpaarPair() {
  const [params] = useSearchParams();
  const draft = loadWordPairDraft();
  const [mode, setMode] = useState<PairMode>(() =>
    parseMode(new URLSearchParams(window.location.hash.split("?")[1] ?? "").get("mode")),
  );
  const [wordA, setWordA] = useState(draft?.wordA ?? "Listen");
  const [wordB, setWordB] = useState(draft?.wordB ?? "Silent");
  const [anagramWord, setAnagramWord] = useState(draft?.wordA ?? "Listen");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [profile] = useState("og");
  const batchSize = useSizeCompare();

  useEffect(() => {
    setMode(parseMode(params.get("mode")));
  }, [params]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setSteps([]);
    batchSize.reset();

    try {
      if (mode === "anagram") {
        if (!anagramWord.trim()) return;
        const resp = await api.anagramSearch(anagramWord.trim(), profile);
        setResult(resp.result as Record<string, unknown>);
        setSteps(resp.steps ?? []);
      } else {
        if (!wordA.trim() || !wordB.trim()) return;
        const resp = await api.wordPair(wordA.trim(), wordB.trim(), profile, mode);
        setResult(resp.result as Record<string, unknown>);
        setSteps(resp.steps ?? []);
      }
    } catch (err) {
      setError(mapApiError(err));
    } finally {
      setLoading(false);
    }
  }

  async function runPairSizeBatch() {
    if (!result || mode === "anagram") return;
    const h1 = String(result.content_hash1 ?? "");
    const h2 = String(result.content_hash2 ?? "");
    if (!h1 || !h2) return;
    await batchSize.run(() => fetchSizeEncodeBatch([h1, h2], profile));
  }

  return {
    mode,
    setMode,
    wordA,
    setWordA,
    wordB,
    setWordB,
    anagramWord,
    setAnagramWord,
    loading,
    error,
    result,
    steps,
    profile,
    batchSize,
    submit,
    runPairSizeBatch,
    showResult: Boolean(result) && !loading,
  };
}
