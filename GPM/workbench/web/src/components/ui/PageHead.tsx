import type { ReactNode } from "react";

interface PageHeadProps {
  title: string;
  lead?: string;
  help?: ReactNode;
}

export function PageHead({ title, lead, help }: PageHeadProps) {
  return (
    <header className="gpm-page-head">
      <h1 className="gpm-page-head__title">{title}</h1>
      {lead ? <p className="gpm-page-head__lead">{lead}</p> : null}
      {help}
    </header>
  );
}
