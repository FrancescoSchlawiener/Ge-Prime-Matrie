import { useCallback, useState } from "react";
import { api } from "../../api/client";
import { t } from "../../i18n/t";
import { SizeCompareView } from "./SizeCompareView";
import type { SizeComparisonData } from "./sizeFormatters";

export function useSizeCompare() {
  const [data, setData] = useState<SizeComparisonData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async (loader: () => Promise<SizeComparisonData>) => {
    setLoading(true);
    setError(null);
    try {
      const result = await loader();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, run, reset };
}

interface SizeComparePanelProps {
  data: SizeComparisonData | null;
  loading: boolean;
  error: string | null;
}

export function SizeComparePanel({ data, loading, error }: SizeComparePanelProps) {
  if (loading) {
    return <p className="gpm-metric__hint">{t("result.actions.sizeLoading")}</p>;
  }
  if (error) {
    return <div className="gpm-error">{error}</div>;
  }
  if (!data) return null;
  return <SizeCompareView data={data} />;
}

export async function fetchSizeEncodeWord(
  contentHash: string,
  profile: string,
  fallback?: { original: string; normalized: string; substance: number; perm_index: number },
): Promise<SizeComparisonData> {
  const resp = await api.sizeEncodeWord(contentHash, profile, fallback);
  return resp.result as unknown as SizeComparisonData;
}

export async function fetchSizeEncodeBatch(
  wordHashes: string[],
  profile: string,
): Promise<SizeComparisonData> {
  const resp = await api.sizeEncodeBatch(wordHashes, profile);
  return resp.result as unknown as SizeComparisonData;
}

export async function fetchSizeDecodeWord(
  contentHash: string,
  profile: string,
  fallback?: { substance: number; perm_index: number },
): Promise<SizeComparisonData> {
  const resp = await api.sizeDecode(contentHash, profile, fallback);
  return resp.result as unknown as SizeComparisonData;
}
