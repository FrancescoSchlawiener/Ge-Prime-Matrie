interface FormulaBlockProps {
  formula: string;
}

export function FormulaBlock({ formula }: FormulaBlockProps) {
  return <pre className="formula-block">{formula}</pre>;
}
