export type ExplainSection = "grundlagen" | "vergleich" | "dokument" | "analyse" | "code" | "tensorraum";

export interface ExplainWorkbenchStep {
  where: string;
  action: string;
  outcome: string;
}

export interface ExplainExampleRow {
  label: string;
  value: string;
  kind?: "S" | "N" | "D" | "H" | "C";
}

export interface ExplainExampleBlock {
  title?: string;
  code?: string;
  rows: ExplainExampleRow[];
}

export type ExplainCtaType = "encode" | "decode" | "compare" | "gpm" | "ikurve" | "tensorraum";

export interface ExplainArticleMeta {
  slug: string;
  section: ExplainSection;
  title: string;
  summary: string;
  atAGlance: string[];
  workbench?: ExplainWorkbenchStep[];
  workbenchTip?: string;
  examples?: ExplainExampleBlock[];
  related?: string[];
  cta?: {
    type: ExplainCtaType;
    demoText?: string;
    wordA?: string;
    wordB?: string;
  };
  miniCalc?: "encode" | "decode" | "compare";
  showSiFormula?: boolean;
}

export const EXPLAIN_SECTIONS: { id: ExplainSection; labelKey: string }[] = [
  { id: "grundlagen", labelKey: "explain.sections.grundlagen" },
  { id: "vergleich", labelKey: "explain.sections.vergleich" },
  { id: "dokument", labelKey: "explain.sections.dokument" },
  { id: "analyse", labelKey: "explain.sections.analyse" },
  { id: "code", labelKey: "explain.sections.code" },
  { id: "tensorraum", labelKey: "explain.sections.tensorraum" },
];

export { EXPLAIN_SLUG_REDIRECTS, resolveExplainSlug } from "./explain-redirects";
export { EXPLAIN_ARTICLES_DATA } from "./articles-data";

import { EXPLAIN_ARTICLES_DATA } from "./articles-data";

export const EXPLAIN_ARTICLES: ExplainArticleMeta[] = EXPLAIN_ARTICLES_DATA;

export function getExplainArticle(slug: string): ExplainArticleMeta | undefined {
  return EXPLAIN_ARTICLES.find((a) => a.slug === slug);
}

export function getExplainNeighbors(slug: string): {
  prev?: ExplainArticleMeta;
  next?: ExplainArticleMeta;
} {
  const idx = EXPLAIN_ARTICLES.findIndex((a) => a.slug === slug);
  if (idx < 0) return {};
  return {
    prev: idx > 0 ? EXPLAIN_ARTICLES[idx - 1] : undefined,
    next: idx < EXPLAIN_ARTICLES.length - 1 ? EXPLAIN_ARTICLES[idx + 1] : undefined,
  };
}

export function getArticlesBySection(section: ExplainSection): ExplainArticleMeta[] {
  return EXPLAIN_ARTICLES.filter((a) => a.section === section);
}
