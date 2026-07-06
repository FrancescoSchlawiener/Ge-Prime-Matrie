export interface SummaryItem {
  label: string;
  value: string;
  mono?: boolean;
}

interface SummaryStripProps {
  items: SummaryItem[];
}

export function SummaryStrip({ items }: SummaryStripProps) {
  return (
    <div className="gpm-summary-strip">
      {items.map((item) => (
        <div key={item.label} className="gpm-summary-box">
          <span className="gpm-summary-box__label">{item.label}</span>
          <span className={`gpm-summary-box__value${item.mono ? " mono" : ""}`}>{item.value}</span>
        </div>
      ))}
    </div>
  );
}
