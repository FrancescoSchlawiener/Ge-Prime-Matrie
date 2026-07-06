import { useState } from "react";
import { api } from "../../api/client";
import { t } from "../../i18n/t";
import { Button, Input } from "../ui";
import { StepList } from "../steps/StepList";

interface ExplainMiniCalcProps {
  kind: string;
}

export function ExplainMiniCalc({ kind }: ExplainMiniCalcProps) {
  const [word, setWord] = useState("HALLO");
  const [substance, setSubstance] = useState("2");
  const [index, setIndex] = useState("0");
  const [b, setB] = useState("SILENT");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<import("../../api/gpm-api").Step[]>([]);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      let resp;
      if (kind === "decode") {
        resp = await api.decodeWord(Number(substance), Number(index), "og", false);
      } else if (kind === "compare") {
        resp = await api.compareWords(word, b, "og", false);
      } else {
        resp = await api.encodeWord(word, "og", false);
      }
      setSteps(resp.steps);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ marginTop: "1rem" }}>
      <h3 className="gpm-card__title">{t("explain.miniCalc.title")}</h3>
      {error ? <div className="gpm-error">{error}</div> : null}
      {kind !== "decode" && kind !== "compare" ? (
        <Input value={word} onChange={(e) => setWord(e.target.value)} />
      ) : null}
      {kind === "compare" ? <Input value={b} onChange={(e) => setB(e.target.value)} /> : null}
      {kind === "decode" ? (
        <>
          <Input value={substance} onChange={(e) => setSubstance(e.target.value)} placeholder="S" />
          <Input value={index} onChange={(e) => setIndex(e.target.value)} placeholder="I" />
        </>
      ) : null}
      <div style={{ marginTop: "0.5rem" }}>
        <Button onClick={run} disabled={loading}>
          {t("explain.miniCalc.run")}
        </Button>
      </div>
      <StepList steps={steps} />
    </div>
  );
}
