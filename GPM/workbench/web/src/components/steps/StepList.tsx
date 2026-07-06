import type { Step } from "../../api/gpm-api";
import { t } from "../../i18n/t";
import { StepCard } from "./StepCard";

interface StepListProps {
  steps: Step[];
}

export function StepList({ steps }: StepListProps) {
  if (!steps.length) return null;
  return (
    <div style={{ marginTop: "1rem" }}>
      <h3 className="gpm-card__title">{t("shell.common.steps")}</h3>
      {steps.map((s) => (
        <StepCard key={s.id} step={s} />
      ))}
    </div>
  );
}
