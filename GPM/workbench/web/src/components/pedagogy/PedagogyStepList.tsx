import type { Step } from "../../api/gpm-api";
import { DataBlock } from "./DataBlock";
import { FormulaBox } from "./FormulaBox";

interface PedagogyStepListProps {
  steps: Step[];
  variant?: "decode" | "encode";
}

export function PedagogyStepList({ steps, variant = "decode" }: PedagogyStepListProps) {
  if (!steps.length) return null;

  return (
    <ol className="gpm-step-list">
      {steps.map((step, idx) => (
        <li key={step.id} className={`gpm-step gpm-step--${variant}`}>
          <div className="gpm-step__head">
            <span className="gpm-step__num">{idx + 1}</span>
            <div>
              <div className="gpm-step__title">{step.title}</div>
              <p className="gpm-step__detail">{step.detail}</p>
            </div>
          </div>
          {step.lines?.length ? (
            <DataBlock>
              {step.lines.map((line, i) => (
                <li key={i}>{line}</li>
              ))}
            </DataBlock>
          ) : null}
          {step.formula ? <FormulaBox formula={step.formula} /> : null}
          {step.extra ? <p className="gpm-step__extra">{step.extra}</p> : null}
        </li>
      ))}
    </ol>
  );
}
