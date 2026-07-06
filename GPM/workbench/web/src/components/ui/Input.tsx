import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export function Input({ label, id, className = "", ...rest }: InputProps) {
  const inputId = id ?? rest.name;
  return (
    <label className="gpm-field" htmlFor={inputId}>
      {label ? <span className="gpm-label">{label}</span> : null}
      <input id={inputId} className={`gpm-input ${className}`.trim()} {...rest} />
    </label>
  );
}
