import type { TextareaHTMLAttributes } from "react";

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
}

export function TextArea({ label, id, className = "", ...rest }: TextAreaProps) {
  const areaId = id ?? rest.name;
  return (
    <label className="gpm-field" htmlFor={areaId}>
      {label ? <span className="gpm-label">{label}</span> : null}
      <textarea id={areaId} className={`gpm-textarea ${className}`.trim()} {...rest} />
    </label>
  );
}
