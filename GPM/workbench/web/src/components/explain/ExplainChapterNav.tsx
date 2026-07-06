import { Link } from "react-router-dom";
import type { ExplainArticleMeta } from "@gpm/ui-text/articles";
import { t } from "../../i18n/t";

interface ExplainChapterNavProps {
  prev?: ExplainArticleMeta;
  next?: ExplainArticleMeta;
}

export function ExplainChapterNav({ prev, next }: ExplainChapterNavProps) {
  if (!prev && !next) return null;
  return (
    <nav className="gpm-explain-chapter-nav" aria-label="Kapitelwechsel">
      {prev ? (
        <Link to={`/erklaerungen/${prev.slug}`} className="gpm-explain-chapter-nav__link gpm-explain-chapter-nav__link--prev">
          <span className="gpm-explain-chapter-nav__dir">{t("explain.nav.prev")}</span>
          <span className="gpm-explain-chapter-nav__title">
            {prev.slug.slice(0, 2)} — {prev.title}
          </span>
        </Link>
      ) : (
        <span />
      )}
      {next ? (
        <Link to={`/erklaerungen/${next.slug}`} className="gpm-explain-chapter-nav__link gpm-explain-chapter-nav__link--next">
          <span className="gpm-explain-chapter-nav__dir">{t("explain.nav.next")}</span>
          <span className="gpm-explain-chapter-nav__title">
            {next.slug.slice(0, 2)} — {next.title}
          </span>
        </Link>
      ) : null}
    </nav>
  );
}
