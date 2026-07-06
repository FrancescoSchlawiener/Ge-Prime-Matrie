import { Navigate, useParams } from "react-router-dom";
import { EXPLAIN_ARTICLES, resolveExplainSlug } from "../content";
import { ExplainSidebar } from "../components/explain/ExplainSidebar";
import { ExplainArticle } from "../components/explain/ExplainArticle";

export function ErklaerungenPage() {
  const { chapter: rawChapter } = useParams();
  const chapter = rawChapter ?? "00-einstieg";
  const resolved = resolveExplainSlug(chapter);

  if (resolved !== chapter) {
    return <Navigate to={`/erklaerungen/${resolved}`} replace />;
  }

  const meta = EXPLAIN_ARTICLES.find((a) => a.slug === resolved) ?? EXPLAIN_ARTICLES[0];

  return (
    <div className="gpm-explain-layout">
      <ExplainSidebar />
      <ExplainArticle meta={meta} />
    </div>
  );
}
