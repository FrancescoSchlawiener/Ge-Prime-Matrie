import { Link } from "react-router-dom";
import type { ExplainArticleMeta } from "@gpm/ui-text/articles";
import { EXPLAIN_SECTIONS } from "@gpm/ui-text/articles";
import { t } from "../../i18n/t";

interface ExplainChapterHeroProps {
  meta: ExplainArticleMeta;
  prev?: ExplainArticleMeta;
  next?: ExplainArticleMeta;
}

function sectionLabel(section: ExplainArticleMeta["section"]): string {
  const found = EXPLAIN_SECTIONS.find((s) => s.id === section);
  return found ? t(found.labelKey) : section;
}

export function ExplainChapterHero({ meta, prev, next }: ExplainChapterHeroProps) {
  const num = meta.slug.slice(0, 2);
  return (
    <header className="gpm-explain-hero">
      <div className="gpm-explain-hero__top">
        <span className="gpm-explain-hero__badge">{sectionLabel(meta.section)}</span>
        <span className="gpm-explain-hero__meta">
          {t("explain.chapter.label")} {num}
        </span>
        <nav className="gpm-explain-hero__nav" aria-label="Kapitelnavigation">
          {prev ? (
            <Link to={`/erklaerungen/${prev.slug}`} className="gpm-explain-hero__nav-link">
              ← {prev.title}
            </Link>
          ) : (
            <span />
          )}
          {next ? (
            <Link to={`/erklaerungen/${next.slug}`} className="gpm-explain-hero__nav-link">
              {next.title} →
            </Link>
          ) : null}
        </nav>
      </div>
      <h1 className="gpm-explain-hero__title">{meta.title}</h1>
      <p className="gpm-explain-hero__summary">{meta.summary}</p>
    </header>
  );
}
