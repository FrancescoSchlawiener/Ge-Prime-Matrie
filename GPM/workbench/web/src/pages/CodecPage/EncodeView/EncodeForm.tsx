import { Button, Card, TextArea } from "../../../components/ui";
import { t } from "../../../i18n/t";

interface EncodeFormProps {
  text: string;
  loading: boolean;
  onTextChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function EncodeForm({ text, loading, onTextChange, onSubmit }: EncodeFormProps) {
  return (
    <Card>
      <form onSubmit={onSubmit}>
        <TextArea
          label={t("encode.wordsLabel")}
          value={text}
          onChange={(e) => onTextChange(e.target.value)}
          placeholder={t("encode.wordsPlaceholder")}
          rows={6}
        />
        <p className="gpm-metric__hint" style={{ marginTop: "0.5rem" }}>
          {t("encode.hint")}
        </p>
        <div className="gpm-form-row" style={{ marginTop: "1rem" }}>
          <Button type="submit" disabled={loading}>
            {loading ? "…" : t("encode.submit")}
          </Button>
        </div>
      </form>
    </Card>
  );
}
