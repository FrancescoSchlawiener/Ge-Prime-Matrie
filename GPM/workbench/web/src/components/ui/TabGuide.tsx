import type { ReactNode } from "react";

interface TabGuideProps {
  children: ReactNode;
}

export function TabGuide({ children }: TabGuideProps) {
  return <aside className="gpm-tab-guide">{children}</aside>;
}
