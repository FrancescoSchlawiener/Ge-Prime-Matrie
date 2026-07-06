import { useState } from "react";
import { api } from "../../api/client";
import { t } from "../../i18n/t";
import { Button, Input, SegmentToggle } from "../../components/ui";
import { formatBigInt } from "../../utils/format";

type SearchMode = "word" | "gcd" | "lcm";

interface GpmSearchPanelProps {
  documentRef: string | null;
}

export function GpmSearchPanel({ documentRef }: GpmSearchPanelProps) {
  const [mode, setMode] = useState<SearchMode>("word");
  const [query, setQuery] = useState("");
  const [query2, setQuery2] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function search() {
    if (!documentRef) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await api.gpmSearch(
        documentRef,
        query,
        mode,
        mode === "lcm" ? [query, query2].filter(Boolean) : undefined,
      );
      setResult(resp.result as Record<string, unknown>);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <details className="gpm-search-panel">
      <summary className="gpm-search-panel__summary">{t("gpm.searchPanel.summary")}</summary>
      <div className="gpm-search-panel__body">
        {!documentRef ? <p className="gpm-metric__hint">{t("gpm.empty")}</p> : null}
        <SegmentToggle
          name="gpm-search-mode"
          value={mode}
          onChange={(v) => setMode(v as SearchMode)}
          options={[
            { value: "word", label: t("gpm.searchModes.substance") },
            { value: "gcd", label: t("gpm.searchModes.gcd") },
            { value: "lcm", label: t("gpm.searchModes.lcm") },
          ]}
        />
        <div style={{ marginTop: "1rem" }}>
          <Input label={t("gpm.searchQuery")} value={query} onChange={(e) => setQuery(e.target.value)} />
          {mode === "lcm" ? (
            <div style={{ marginTop: "0.5rem" }}>
              <Input label={t("gpm.searchQuery2")} value={query2} onChange={(e) => setQuery2(e.target.value)} />
            </div>
          ) : null}
        </div>
        <div style={{ marginTop: "1rem" }}>
          <Button onClick={() => void search()} disabled={loading || !documentRef}>
            {t("gpm.searchSubmit")}
          </Button>
        </div>
        {error ? <div className="gpm-error" style={{ marginTop: "0.5rem" }}>{error}</div> : null}
        {result ? <SearchResult mode={mode} result={result} /> : null}
      </div>
    </details>
  );
}

function SearchResult({ mode, result }: { mode: SearchMode; result: Record<string, unknown> }) {
  if (mode === "word") {
    const positions = (result.positions as Array<Record<string, unknown>>) ?? [];
    return (
      <div className="gpm-table-wrap" style={{ marginTop: "1rem" }}>
        <p className="gpm-metric__hint">
          {String(result.occurrences ?? 0)} {t("gpm.searchHits")}
        </p>
        <table className="gpm-table">
          <thead>
            <tr>
              <th>{t("gpm.tables.position")}</th>
              <th>word_id</th>
              <th>I</th>
            </tr>
          </thead>
          <tbody>
            {positions.slice(0, 30).map((p, i) => (
              <tr key={i}>
                <td>{String(p.position)}</td>
                <td>{String(p.word_id)}</td>
                <td className="mono">{String(p.perm_index)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  const matches = (result.matches as Array<Record<string, unknown>>) ?? [];
  return (
    <div className="gpm-table-wrap" style={{ marginTop: "1rem" }}>
      <p className="gpm-metric__hint">
        {formatBigInt(Number(result.unique_words ?? matches.length))} {t("gpm.searchMatches")}
      </p>
      <table className="gpm-table">
        <thead>
          <tr>
            <th>{t("gpm.tables.word")}</th>
            <th>S</th>
            {mode === "gcd" ? <th>ggT</th> : null}
          </tr>
        </thead>
        <tbody>
          {matches.slice(0, 30).map((m, i) => (
            <tr key={i}>
              <td>{String(m.normalized ?? m.original ?? "—")}</td>
              <td className="mono">{String(m.substance ?? "—")}</td>
              {mode === "gcd" ? <td className="mono">{String(m.gcd_value ?? "—")}</td> : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
