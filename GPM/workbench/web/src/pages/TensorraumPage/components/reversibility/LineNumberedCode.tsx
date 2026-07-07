import { formatCodeWithLineNumbers } from "../../../../lib/tensorraum";

interface LineNumberedCodeProps {
  code: string;
  label: string;
  failed?: boolean;
}

export function LineNumberedCode({ code, label, failed = false }: LineNumberedCodeProps) {
  const numbered = formatCodeWithLineNumbers(code);
  const stateClass = failed ? " gpm-tensor-reversibility-code--fail" : " gpm-tensor-reversibility-code--ok";

  return (
    <div className={`gpm-tensor-reversibility-code${stateClass}`}>
      <div className="gpm-tensor-reversibility-code__label">{label}</div>
      <pre className="gpm-tensor-reversibility-code__pre">{numbered || " "}</pre>
    </div>
  );
}
