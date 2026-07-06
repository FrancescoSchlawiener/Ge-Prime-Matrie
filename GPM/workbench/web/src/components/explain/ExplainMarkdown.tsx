import { useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
import { t } from "../../i18n/t";

export interface TocEntry {
  id: string;
  text: string;
  level: number;
}

interface ExplainMarkdownProps {
  body: string;
  onHeadings?: (entries: TocEntry[]) => void;
}

function extractHeadings(body: string): TocEntry[] {
  const entries: TocEntry[] = [];
  for (const line of body.split("\n")) {
    const m = /^(#{2,3})\s+(.+)$/.exec(line.trim());
    if (!m) continue;
    const text = m[2].replace(/\*\*/g, "").replace(/`/g, "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").trim();
    const id = text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-");
    entries.push({ id, text, level: m[1].length });
  }
  return entries;
}

export function ExplainMarkdown({ body, onHeadings }: ExplainMarkdownProps) {
  const headings = useMemo(() => extractHeadings(body), [body]);

  useEffect(() => {
    onHeadings?.(headings);
  }, [headings, onHeadings]);

  return (
    <div className="gpm-explain-article-body">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSlug]}
        components={{
          table: ({ children }) => <table className="gpm-explain-table">{children}</table>,
          blockquote: ({ children }) => <blockquote className="gpm-explain-callout">{children}</blockquote>,
          a: ({ href, children }) => {
            if (href?.startsWith("/erklaerungen/")) {
              return (
                <Link to={href} className="gpm-explain-article-body__link">
                  {children}
                </Link>
              );
            }
            return <a href={href}>{children}</a>;
          },
        }}
      >
        {body}
      </ReactMarkdown>
    </div>
  );
}

interface ExplainTableOfContentsProps {
  entries: TocEntry[];
}

export function ExplainTableOfContents({ entries }: ExplainTableOfContentsProps) {
  if (entries.length < 2) return null;
  return (
    <nav className="gpm-explain-toc" aria-label={t("explain.toc.title")}>
      <h3 className="gpm-explain-toc__title">{t("explain.toc.title")}</h3>
      <ul className="gpm-explain-toc__list">
        {entries.map((e) => (
          <li key={e.id} className={`gpm-explain-toc__item gpm-explain-toc__item--h${e.level}`}>
            <a href={`#${e.id}`} className="gpm-explain-toc__link">
              {e.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
