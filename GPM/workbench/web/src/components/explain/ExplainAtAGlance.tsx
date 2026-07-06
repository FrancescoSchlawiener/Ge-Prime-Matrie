import { t } from "../../i18n/t";

interface ExplainAtAGlanceProps {
  items: string[];
}

export function ExplainAtAGlance({ items }: ExplainAtAGlanceProps) {
  if (!items.length) return null;
  return (
    <section className="gpm-explain-glance" aria-labelledby="explain-glance-title">
      <h2 id="explain-glance-title" className="gpm-explain-glance__title">
        {t("explain.glance.title")}
      </h2>
      <div className="gpm-explain-glance__grid">
        {items.map((text) => (
          <div key={text} className="gpm-explain-glance__card">
            {text}
          </div>
        ))}
      </div>
    </section>
  );
}
