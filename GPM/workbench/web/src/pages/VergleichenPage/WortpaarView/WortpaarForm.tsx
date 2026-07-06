import { Button, Card, Input, SegmentToggle } from "../../../components/ui";
import { t } from "../../../i18n/t";
import { helpBody, helpTitle, submitLabel, type PairMode } from "./wortpaarMode";

interface WortpaarFormProps {
  mode: PairMode;
  wordA: string;
  wordB: string;
  anagramWord: string;
  loading: boolean;
  onModeChange: (m: PairMode) => void;
  onWordAChange: (v: string) => void;
  onWordBChange: (v: string) => void;
  onAnagramWordChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function WortpaarForm({
  mode,
  wordA,
  wordB,
  anagramWord,
  loading,
  onModeChange,
  onWordAChange,
  onWordBChange,
  onAnagramWordChange,
  onSubmit,
}: WortpaarFormProps) {
  return (
    <Card>
      <form onSubmit={onSubmit}>
        <SegmentToggle
          name="pair-mode"
          value={mode}
          aria-label={t("wortpaar.modeAria")}
          options={[
            { value: "compare", label: t("wortpaar.modes.compareFull") },
            { value: "diff", label: t("wortpaar.modes.diffFull") },
            { value: "anagram", label: t("wortpaar.modes.anagram") },
          ]}
          onChange={(v) => onModeChange(v as PairMode)}
        />
        <details className="gpm-mode-help" style={{ marginTop: "0.75rem" }}>
          <summary>{helpTitle(mode)}</summary>
          <p>{helpBody(mode)}</p>
        </details>
        {mode === "anagram" ? (
          <div style={{ marginTop: "1rem" }}>
            <Input
              label={t("wortpaar.anagramWord")}
              value={anagramWord}
              onChange={(e) => onAnagramWordChange(e.target.value)}
              placeholder={t("wortpaar.anagramWordPlaceholder")}
            />
          </div>
        ) : (
          <div className="gpm-word-pair" style={{ marginTop: "1rem" }}>
            <Input
              label={t("wortpaar.wordA")}
              value={wordA}
              onChange={(e) => onWordAChange(e.target.value)}
              placeholder={t("wortpaar.wordAPlaceholder")}
            />
            <Input
              label={t("wortpaar.wordB")}
              value={wordB}
              onChange={(e) => onWordBChange(e.target.value)}
              placeholder={t("wortpaar.wordBPlaceholder")}
            />
          </div>
        )}
        <div style={{ marginTop: "1rem" }}>
          <Button type="submit" disabled={loading}>
            {loading ? t("wortpaar.loading") : submitLabel(mode)}
          </Button>
        </div>
      </form>
    </Card>
  );
}
