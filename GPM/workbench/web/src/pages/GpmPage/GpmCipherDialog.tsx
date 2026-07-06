import { t } from "../../i18n/t";
import { Button, Dialog, Input, SegmentToggle } from "../../components/ui";
import type { CipherDialogMode, CipherMode } from "./useGpmDocument";

interface GpmCipherDialogProps {
  open: boolean;
  mode: CipherDialogMode;
  cipherMode: CipherMode;
  cipherKey: string;
  cipherOut: string | null;
  loading: boolean;
  onModeChange: (m: CipherMode) => void;
  onKeyChange: (k: string) => void;
  onSubmit: () => void;
  onClose: () => void;
}

export function GpmCipherDialog({
  open,
  mode,
  cipherMode,
  cipherKey,
  cipherOut,
  loading,
  onModeChange,
  onKeyChange,
  onSubmit,
  onClose,
}: GpmCipherDialogProps) {
  return (
    <Dialog open={open} title={t("gpm.cipherDialog.title")} onClose={onClose}>
      <p className="gpm-metric__hint">
        {mode === "decrypt" ? t("gpm.cipherDialog.decryptHint") : t("gpm.cipherDialog.encryptHint")}
      </p>
      {mode === "encrypt" ? (
        <SegmentToggle
          name="cipher-mode"
          value={cipherMode}
          onChange={(v) => onModeChange(v as CipherMode)}
          options={[
            { value: "word", label: t("gpm.cipherModes.word") },
            { value: "prime", label: t("gpm.cipherModes.prime") },
            { value: "si", label: t("gpm.cipherModes.si") },
            { value: "hardcore", label: t("gpm.cipherModes.hardcore") },
          ]}
        />
      ) : null}
      <Input label={t("gpm.keyLabel")} value={cipherKey} onChange={(e) => onKeyChange(e.target.value)} />
      {cipherOut ? (
        <p className="mono gpm-metric__hint" style={{ wordBreak: "break-all" }}>
          {cipherOut.length > 200 ? `${cipherOut.slice(0, 200)}…` : cipherOut}
        </p>
      ) : null}
      <div className="gpm-dialog__actions">
        <Button variant="ghost" onClick={onClose}>
          {t("gpm.cipherDialog.cancel")}
        </Button>
        <Button onClick={onSubmit} disabled={loading || !cipherKey.trim()}>
          {t("gpm.cipherDialog.submit")}
        </Button>
      </div>
    </Dialog>
  );
}
