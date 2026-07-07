import { Link } from "react-router-dom";
import { ExplainMarkdown } from "../../../components/explain/ExplainMarkdown";
import { DisclosureSection } from "../../../components/ui/DisclosureSection";
import { getArticleBody } from "../../../content";
import { t } from "../../../i18n/t";

const TENSORRAUM_EXPLAIN_SLUG = "29-tensorraum";

export function TensorraumDocsPanel() {
  const body = getArticleBody(TENSORRAUM_EXPLAIN_SLUG);
  if (!body) return null;

  return (
    <div className="gpm-tensor-docs">
      <DisclosureSection
        title={t("tensorraum.explain.panelTitle")}
        brief={t("tensorraum.explain.panelBrief")}
        defaultOpen={false}
      >
        <ExplainMarkdown body={body} />
        <p className="gpm-tensor-docs__link">
          <Link to={`/erklaerungen/${TENSORRAUM_EXPLAIN_SLUG}`}>{t("tensorraum.explain.openChapter")}</Link>
        </p>
      </DisclosureSection>
    </div>
  );
}
