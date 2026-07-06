import type { Step } from "../../api/gpm-api";
import { StepValues } from "./StepValues";

interface StepCardProps {
  step: Step;
}

export function StepCard({ step }: StepCardProps) {
  return (
    <article className="gpm-card" style={{ marginTop: "0.5rem", padding: "0.75rem 1rem" }}>
      <h4 className="gpm-card__title">{step.title}</h4>
      <p className="gpm-metric__hint">{step.detail}</p>
      {step.formula ? <code className="mono">{step.formula}</code> : null}
      <StepValues values={step.values} />
    </article>
  );
}
