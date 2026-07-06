import { Button, Card, Input } from "../../../components/ui";
import { t } from "../../../i18n/t";

interface DecodeFormProps {
  substance: string;
  index: string;
  loading: boolean;
  onSubstanceChange: (v: string) => void;
  onIndexChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function DecodeForm({
  substance,
  index,
  loading,
  onSubstanceChange,
  onIndexChange,
  onSubmit,
}: DecodeFormProps) {
  return (
    <Card>
      <form onSubmit={onSubmit}>
        <div className="gpm-word-pair">
          <Input
            label={t("decode.substanceLabel")}
            value={substance}
            onChange={(e) => onSubstanceChange(e.target.value)}
            placeholder={t("decode.substancePlaceholder")}
            inputMode="numeric"
            autoComplete="off"
          />
          <Input
            label={t("decode.indexLabel")}
            value={index}
            onChange={(e) => onIndexChange(e.target.value)}
            placeholder={t("decode.indexPlaceholder")}
            inputMode="numeric"
            autoComplete="off"
          />
        </div>
        <p className="gpm-metric__hint" style={{ marginTop: "0.75rem" }}>
          {t("decode.tip")}
        </p>
        <div style={{ marginTop: "1rem" }}>
          <Button type="submit" disabled={loading}>
            {loading ? "…" : t("decode.submit")}
          </Button>
        </div>
      </form>
    </Card>
  );
}
