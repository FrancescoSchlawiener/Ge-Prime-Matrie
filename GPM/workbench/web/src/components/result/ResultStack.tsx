import type { ReactNode } from "react";

interface ResultStackProps {
  children: ReactNode;
}

export function ResultStack({ children }: ResultStackProps) {
  return <div className="gpm-result-stack">{children}</div>;
}
