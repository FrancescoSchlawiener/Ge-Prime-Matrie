interface StepValuesProps {
  values?: Record<string, string | number | boolean>;
}

export function StepValues({ values }: StepValuesProps) {
  if (!values || !Object.keys(values).length) return null;
  return (
    <div className="step-values">
      {Object.entries(values).map(([k, v]) => (
        <span key={k} className="step-values__item">
          {k}={String(v)}
        </span>
      ))}
    </div>
  );
}
