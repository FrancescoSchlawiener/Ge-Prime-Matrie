import type { ReactNode } from "react";

interface DataBlockProps {
  children: ReactNode;
  as?: "ul" | "div";
}

export function DataBlock({ children, as = "ul" }: DataBlockProps) {
  const className = "gpm-data-block mono";
  if (as === "div") {
    return <div className={className}>{children}</div>;
  }
  return <ul className={`${className} gpm-step-lines`}>{children}</ul>;
}
