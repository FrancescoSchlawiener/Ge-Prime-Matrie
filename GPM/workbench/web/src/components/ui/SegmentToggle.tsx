interface SegmentOption<T extends string> {
  value: T;
  label: string;
}

interface SegmentToggleProps<T extends string> {
  name: string;
  value: T;
  options: SegmentOption<T>[];
  onChange: (value: T) => void;
  "aria-label"?: string;
}

export function SegmentToggle<T extends string>({
  name,
  value,
  options,
  onChange,
  "aria-label": ariaLabel,
}: SegmentToggleProps<T>) {
  return (
    <fieldset className="gpm-segment" role="radiogroup" aria-label={ariaLabel}>
      {options.map((opt) => (
        <label key={opt.value} className="gpm-segment__option">
          <input
            type="radio"
            name={name}
            value={opt.value}
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
          />
          <span className="gpm-segment__label">{opt.label}</span>
        </label>
      ))}
    </fieldset>
  );
}
