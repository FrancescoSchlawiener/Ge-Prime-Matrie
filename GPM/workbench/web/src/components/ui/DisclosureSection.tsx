import { useState, type ReactNode, type SyntheticEvent } from "react";
import { t } from "../../i18n/t";

export type DisclosureLevel = "card" | "nested";

interface DisclosureSectionProps {
  title: string;
  brief?: string;
  defaultOpen?: boolean;
  level?: DisclosureLevel;
  children: ReactNode;
}

export function DisclosureSection({
  title,
  brief,
  defaultOpen = false,
  level = "card",
  children,
}: DisclosureSectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  const levelClass = level === "nested" ? " gpm-disclosure--nested" : "";

  function handleToggle(event: SyntheticEvent<HTMLDetailsElement>) {
    setOpen(event.currentTarget.open);
  }

  return (
    <details
      className={`gpm-disclosure${levelClass}`}
      open={open}
      onToggle={handleToggle}
    >
      <summary className="gpm-disclosure__summary">
        <span className="gpm-disclosure__chevron" aria-hidden>
          ▸
        </span>
        <span className="gpm-disclosure__title">{title}</span>
        {brief ? <span className="gpm-disclosure__brief">{brief}</span> : null}
        <span className="sr-only">
          {open ? t("ikurve.disclosure.collapseHint") : t("ikurve.disclosure.expandHint")}
        </span>
      </summary>
      {open ? <div className="gpm-disclosure__body">{children}</div> : null}
    </details>
  );
}
