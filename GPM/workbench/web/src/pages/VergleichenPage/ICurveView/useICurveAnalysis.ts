import { useEffect, useState } from "react";
import { api } from "../../../api/client";
import type { CurveMeta } from "../../../api/gpm-api";
import type { TokenSelection } from "../../../components/result/ikurve/GeometricMatrix";
import { expandSpectroMatches, mergeSpectroMatches } from "../../../lib/ikurve/spectro";
import type { SpectroMatch } from "../../../lib/ikurve/spectro";
import type {
  ChartScale,
  IcurveMode,
  IngestSourceMode,
  SemanticDepth,
  StructuralDepth,
} from "../../../lib/ikurve/curves";
import { loadICurveSideA } from "../../../utils/sessionBridge";

export function useICurveAnalysis() {
  const presetA = loadICurveSideA();
  const [textA, setTextA] = useState(presetA ?? "");
  const [textB, setTextB] = useState("");
  const [sourceA, setSourceA] = useState<IngestSourceMode>("text");
  const [sourceB, setSourceB] = useState<IngestSourceMode>("text");
  const [gpmNameA, setGpmNameA] = useState("");
  const [gpmNameB, setGpmNameB] = useState("");
  const [docRefA, setDocRefA] = useState("");
  const [docRefB, setDocRefB] = useState("");
  const [locked, setLocked] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [curveMeta, setCurveMeta] = useState<CurveMeta | null>(null);
  const [openZone, setOpenZone] = useState<string | null>("structure");
  const [mode, setMode] = useState<IcurveMode>("semantic");
  const [depth, setDepth] = useState<SemanticDepth | StructuralDepth>("sentence");
  const [chartScale, setChartScale] = useState<ChartScale>("union");
  const [selA, setSelA] = useState<TokenSelection | null>(null);
  const [selB, setSelB] = useState<TokenSelection | null>(null);
  const [spectroA, setSpectroA] = useState<SpectroMatch[]>([]);
  const [spectroB, setSpectroB] = useState<SpectroMatch[]>([]);

  useEffect(() => {
    if (presetA) setTextA(presetA);
  }, [presetA]);

  async function analyze() {
    if (!textA.trim() || !textB.trim()) return;
    setLoading(true);
    setError(null);
    setSelA(null);
    setSelB(null);
    setSpectroA([]);
    setSpectroB([]);
    try {
      const compA = await api.compile("nl", textA, "og");
      const compB = await api.compile("nl", textB, "og");
      const refA = String((compA.result as { document_ref: string }).document_ref);
      const refB = String((compB.result as { document_ref: string }).document_ref);
      const resp = await api.iCurve(refA, refB);
      setDocRefA(refA);
      setDocRefB(refB);
      setData(resp.result as Record<string, unknown>);
      setCurveMeta(resp.curve_meta ?? null);
      setLocked(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setLocked(false);
    setData(null);
    setCurveMeta(null);
    setDocRefA("");
    setDocRefB("");
    setSelA(null);
    setSelB(null);
    setSpectroA([]);
    setSpectroB([]);
  }

  async function runSpectro(side: "a" | "b") {
    const ref = side === "a" ? docRefA : docRefB;
    const sel = side === "a" ? selA : selB;
    const viewport = side === "a" ? data?.viewport_a : data?.viewport_b;
    if (!ref || !sel) return;
    const tokenEnd = sel.token_start + sel.token_count - 1;
    const resp = await api.spectroscope(ref, sel.token_start, tokenEnd);
    const result = resp.result as Record<string, unknown>;
    const matches = expandSpectroMatches(
      (result.matches as SpectroMatch[]) ?? [],
      ((viewport as { token_char_map?: SpectroMatch[] })?.token_char_map ?? []) as never,
    );
    const merged = mergeSpectroMatches(matches);
    if (side === "a") setSpectroA(merged);
    else setSpectroB(merged);
  }

  return {
    textA,
    setTextA,
    textB,
    setTextB,
    sourceA,
    setSourceA,
    sourceB,
    setSourceB,
    gpmNameA,
    setGpmNameA,
    gpmNameB,
    setGpmNameB,
    locked,
    loading,
    error,
    data,
    curveMeta,
    openZone,
    setOpenZone,
    mode,
    setMode,
    depth,
    setDepth,
    chartScale,
    setChartScale,
    docRefA,
    docRefB,
    selA,
    setSelA,
    selB,
    setSelB,
    spectroA,
    spectroB,
    analyze,
    reset,
    runSpectro,
  };
}
