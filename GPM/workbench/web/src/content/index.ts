export {
  EXPLAIN_ARTICLES,
  EXPLAIN_SECTIONS,
  EXPLAIN_SLUG_REDIRECTS,
  getExplainArticle,
  getExplainNeighbors,
  getArticlesBySection,
  resolveExplainSlug,
  type ExplainArticleMeta,
  type ExplainSection,
  type ExplainWorkbenchStep,
  type ExplainExampleBlock,
  type ExplainExampleRow,
  type ExplainCtaType,
} from "@gpm/ui-text/articles";

const rawModules = import.meta.glob(
  "../../../../ui-text/de/erklaerungen/*.md",
  { query: "?raw", import: "default", eager: true },
) as Record<string, string>;

const FRONTMATTER_RE = /^---\r?\n[\s\S]*?\r?\n---\r?\n?/;

function slugFromPath(path: string): string {
  const name = path.split("/").pop() ?? path;
  return name.replace(/\.md$/, "");
}

function stripFrontmatter(raw: string): string {
  return raw.replace(FRONTMATTER_RE, "").trimStart();
}

function stripLeadingH1(text: string): string {
  return text.replace(/^#\s+[^\n]+\n+/, "");
}

const articleBodies: Record<string, string> = {};
for (const [path, raw] of Object.entries(rawModules)) {
  articleBodies[slugFromPath(path)] = stripLeadingH1(stripFrontmatter(raw));
}

export function getArticleBody(slug: string): string | undefined {
  return articleBodies[slug];
}
