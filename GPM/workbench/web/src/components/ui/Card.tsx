import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  children: ReactNode;
  className?: string;
}

export function Card({ title, children, className = "" }: CardProps) {
  return (
    <article className={`gpm-card ${className}`.trim()}>
      {title ? <h2 className="gpm-card__title">{title}</h2> : null}
      {children}
    </article>
  );
}
