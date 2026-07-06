import { useMemo, useState } from "react";
import { NavLink } from "react-router-dom";
import {
  EXPLAIN_ARTICLES,
  EXPLAIN_SECTIONS,
  type ExplainArticleMeta,
  type ExplainSection,
} from "@gpm/ui-text/articles";
import { t } from "../../i18n/t";
import { Card } from "../ui/Card";
import { Input } from "../ui";

export function ExplainSidebar() {
  const [query, setQuery] = useState("");
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return EXPLAIN_ARTICLES;
    return EXPLAIN_ARTICLES.filter(
      (a) => a.title.toLowerCase().includes(q) || a.slug.toLowerCase().includes(q),
    );
  }, [query]);

  const bySection = useMemo(() => {
    const map = new Map<ExplainSection, ExplainArticleMeta[]>();
    for (const s of EXPLAIN_SECTIONS) map.set(s.id, []);
    for (const a of filtered) {
      map.get(a.section)?.push(a);
    }
    return map;
  }, [filtered]);

  function toggleSection(id: string) {
    setCollapsed((c) => ({ ...c, [id]: !c[id] }));
  }

  return (
    <Card className="gpm-explain-sidebar">
      <h3 className="gpm-card__title">{t("explain.topics.sidebar")}</h3>
      <Input
        className="gpm-explain-sidebar__search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={t("explain.search.placeholder")}
        aria-label={t("explain.search.placeholder")}
      />
      {filtered.length === 0 ? (
        <p className="gpm-explain-sidebar__empty">{t("explain.search.empty")}</p>
      ) : (
        <nav className="gpm-explain-nav">
          {EXPLAIN_SECTIONS.map((section) => {
            const items = bySection.get(section.id) ?? [];
            if (!items.length) return null;
            const isCollapsed = collapsed[section.id];
            return (
              <div key={section.id} className="gpm-explain-nav__group">
                <button
                  type="button"
                  className="gpm-explain-nav__group-head"
                  onClick={() => toggleSection(section.id)}
                  aria-expanded={!isCollapsed}
                >
                  {t(section.labelKey)}
                  <span className="gpm-explain-nav__chevron">{isCollapsed ? "▸" : "▾"}</span>
                </button>
                {!isCollapsed ? (
                  <div className="gpm-explain-nav__group-items">
                    {items.map((a) => (
                      <NavLink
                        key={a.slug}
                        to={`/erklaerungen/${a.slug}`}
                        className={({ isActive }) =>
                          `gpm-explain-nav__link${isActive ? " gpm-explain-nav__link--active" : ""}`
                        }
                      >
                        <span className="gpm-explain-nav__num">{a.slug.slice(0, 2)}</span>
                        {a.title}
                      </NavLink>
                    ))}
                  </div>
                ) : null}
              </div>
            );
          })}
        </nav>
      )}
    </Card>
  );
}
