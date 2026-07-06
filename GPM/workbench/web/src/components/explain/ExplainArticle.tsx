import { useEffect, useState } from "react";
import type { ExplainArticleMeta } from "@gpm/ui-text/articles";
import { EXPLAIN_ARTICLES, getExplainNeighbors } from "@gpm/ui-text/articles";
import { getArticleBody } from "../../content";
import { FormulaBlock } from "./FormulaBlock";
import { ExplainMiniCalc } from "./ExplainMiniCalc";
import { ExplainChapterHero } from "./ExplainChapterHero";
import { ExplainAtAGlance } from "./ExplainAtAGlance";
import { ExplainWorkbenchPanel } from "./ExplainWorkbenchPanel";
import { ExplainExampleBlocks } from "./ExplainExampleBlocks";
import { ExplainChapterNav } from "./ExplainChapterNav";
import { ExplainRelatedLinks } from "./ExplainRelatedLinks";
import { ExplainChapterCta } from "./ExplainChapterCta";
import { ExplainMarkdown, ExplainTableOfContents, type TocEntry } from "./ExplainMarkdown";
import { Card } from "../ui/Card";

interface ExplainArticleProps {
  meta: ExplainArticleMeta;
}

export function ExplainArticle({ meta }: ExplainArticleProps) {
  const body = getArticleBody(meta.slug) ?? meta.summary;
  const { prev, next } = getExplainNeighbors(meta.slug);
  const [toc, setToc] = useState<TocEntry[]>([]);

  useEffect(() => {
    setToc([]);
  }, [meta.slug]);

  return (
    <div className="gpm-explain-article">
      <Card className="gpm-explain-article__card">
        <ExplainChapterHero meta={meta} prev={prev} next={next} />
        <ExplainAtAGlance items={meta.atAGlance} />
        <div className="gpm-explain-article__columns">
          <div className="gpm-explain-article__main">
            <ExplainMarkdown body={body} onHeadings={setToc} />
            <ExplainWorkbenchPanel steps={meta.workbench} tip={meta.workbenchTip} />
            <ExplainExampleBlocks blocks={meta.examples} />
            <ExplainRelatedLinks related={meta.related} articles={EXPLAIN_ARTICLES} />
            {meta.showSiFormula ? (
              <div className="gpm-explain-formula">
                <div className="gpm-header__formula">S = ∏ pᵢ^aᵢ · decode(S,I) → Text</div>
                <FormulaBlock formula="S = ∏ pᵢ^aᵢ  ·  decode(S,I) → Text" />
              </div>
            ) : null}
            {meta.miniCalc ? <ExplainMiniCalc kind={meta.miniCalc} /> : null}
            {meta.cta ? <ExplainChapterCta cta={meta.cta} /> : null}
            <ExplainChapterNav prev={prev} next={next} />
          </div>
          <ExplainTableOfContents entries={toc} />
        </div>
      </Card>
    </div>
  );
}
