interface BatchMetaBarProps {
  primary: string;
  hints?: string[];
  warnings?: string[];
}

export function BatchMetaBar({ primary, hints = [], warnings = [] }: BatchMetaBarProps) {
  return (
    <div className="gpm-batch-meta">
      <span className="gpm-batch-meta__primary">{primary}</span>
      {hints.map((hint) => (
        <span key={hint} className="gpm-batch-meta__hint">
          {hint}
        </span>
      ))}
      {warnings.map((warning) => (
        <span key={warning} className="gpm-batch-meta__warning">
          {warning}
        </span>
      ))}
    </div>
  );
}
