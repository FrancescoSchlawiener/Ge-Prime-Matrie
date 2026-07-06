import type { ReactNode } from "react";

interface ResultPanelProps {
  index?: number;
  title: string;
  brief?: string;
  defaultOpen?: boolean;
  summary?: ReactNode;
  actions?: ReactNode;
  footer?: ReactNode;
  body?: ReactNode;
}

export function ResultPanel({
  index,
  title,
  brief,
  defaultOpen = false,
  summary,
  actions,
  footer,
  body,
}: ResultPanelProps) {
  return (
    <details className="gpm-result-panel" open={defaultOpen}>
      <summary className="gpm-result-panel__summary">
        {index != null ? <span className="gpm-result-panel__index">#{index}</span> : null}
        <span className="gpm-result-panel__title">{title}</span>
        {brief ? <span className="gpm-result-panel__brief mono">{brief}</span> : null}
      </summary>
      <div className="gpm-result-panel__body">
        {summary}
        {actions}
        {footer}
        {body}
      </div>
    </details>
  );
}
