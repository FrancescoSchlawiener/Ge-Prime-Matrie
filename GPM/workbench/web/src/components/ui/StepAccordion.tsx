interface AccordionItem {
  id: string;
  title: string;
  content: React.ReactNode;
}

interface StepAccordionProps {
  items: AccordionItem[];
  openId: string | null;
  onToggle: (id: string) => void;
}

export function StepAccordion({ items, openId, onToggle }: StepAccordionProps) {
  return (
    <div className="gpm-accordion">
      {items.map((item) => {
        const open = openId === item.id;
        return (
          <div key={item.id} className="gpm-accordion__item">
            <button
              type="button"
              className="gpm-accordion__trigger"
              aria-expanded={open}
              onClick={() => onToggle(open ? "" : item.id)}
            >
              {item.title}
            </button>
            {open ? <div className="gpm-accordion__panel">{item.content}</div> : null}
          </div>
        );
      })}
    </div>
  );
}
