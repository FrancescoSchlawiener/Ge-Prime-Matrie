import type { ExplainExampleBlock } from "@gpm/ui-text/articles";
import { t } from "../../i18n/t";

interface ExplainExampleBlocksProps {
  blocks?: ExplainExampleBlock[];
}

const KIND_CLASS: Record<string, string> = {
  S: "gpm-explain-ex__chip--s",
  N: "gpm-explain-ex__chip--n",
  D: "gpm-explain-ex__chip--d",
  H: "gpm-explain-ex__chip--h",
  C: "gpm-explain-ex__chip--c",
};

export function ExplainExampleBlocks({ blocks }: ExplainExampleBlocksProps) {
  if (!blocks?.length) return null;
  return (
    <section className="gpm-explain-ex" aria-labelledby="explain-ex-title">
      <h2 id="explain-ex-title" className="gpm-explain-ex__title">
        {t("explain.example.title")}
      </h2>
      {blocks.map((block) => (
        <div key={block.code ?? block.title ?? block.rows[0]?.label} className="gpm-explain-ex__block">
          {block.title ? <div className="gpm-explain-ex__subtitle">{block.title}</div> : null}
          {block.code ? <pre className="gpm-explain-ex__code">{block.code}</pre> : null}
          <div className="gpm-explain-ex__rows">
            {block.rows.map((row) => (
              <div key={row.label} className="gpm-explain-ex__row">
                <code className="gpm-explain-ex__label">{row.label}</code>
                {row.kind ? (
                  <span className={`gpm-explain-ex__chip ${KIND_CLASS[row.kind] ?? ""}`}>{row.kind}</span>
                ) : null}
                <span className="gpm-explain-ex__value">{row.value}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}
