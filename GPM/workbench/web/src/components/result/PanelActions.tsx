import type { ReactNode } from "react";

interface PanelActionsProps {
  children: ReactNode;
}

export function PanelActions({ children }: PanelActionsProps) {
  return <div className="gpm-panel-actions">{children}</div>;
}
