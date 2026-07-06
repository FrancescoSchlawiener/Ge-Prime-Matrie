import { Link } from "react-router-dom";
import type { ExplainArticleMeta } from "@gpm/ui-text/articles";
import { t } from "../../i18n/t";

interface ExplainRelatedLinksProps {
  related?: string[];
  articles: ExplainArticleMeta[];
}

export function ExplainRelatedLinks({ related, articles }: ExplainRelatedLinksProps) {
  if (!related?.length) return null;
  const bySlug = new Map(articles.map((a) => [a.slug, a]));
  const items = related.map((slug) => bySlug.get(slug)).filter(Boolean) as ExplainArticleMeta[];
  if (!items.length) return null;
  return (
    <section className="gpm-explain-related">
      <h2 className="gpm-explain-related__title">{t("explain.related.title")}</h2>
      <div className="gpm-explain-related__links">
        {items.map((a) => (
          <Link key={a.slug} to={`/erklaerungen/${a.slug}`} className="gpm-explain-related__link">
            {a.slug.slice(0, 2)} — {a.title}
          </Link>
        ))}
      </div>
    </section>
  );
}
