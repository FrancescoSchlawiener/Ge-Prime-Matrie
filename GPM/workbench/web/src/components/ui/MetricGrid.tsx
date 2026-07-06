interface MetricItem {
  label: string;
  value: string;
  hint?: string;
}

export function MetricGrid({ items }: { items: MetricItem[] }) {
  return (
    <dl className="gpm-metric-grid">
      {items.map((item) => (
        <div key={item.label} className="gpm-metric">
          <dt className="gpm-metric__label">{item.label}</dt>
          <dd className="gpm-metric__value">{item.value}</dd>
          {item.hint ? <dd className="gpm-metric__hint">{item.hint}</dd> : null}
        </div>
      ))}
    </dl>
  );
}
