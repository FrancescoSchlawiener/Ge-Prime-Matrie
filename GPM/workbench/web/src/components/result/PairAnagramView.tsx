import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../ui";
import { t } from "../../i18n/t";
import { languageLabel } from "../../i18n/languageLabel";
import { formatBigInt } from "../../utils/format";
import { saveDecodeDraft } from "../../utils/sessionBridge";
import { PairWordCard } from "./PairWordCard";
import {
  fetchSizeEncodeWord,
  SizeComparePanel,
  useSizeCompare,
} from "./SizeCompareSlot";

interface AnagramHit {
  word_original: string;
  word_normalized: string;
  substance: number;
  perm_index: number;
  language: string;
}

interface LanguageGroup {
  language: string;
  hits: AnagramHit[];
}

interface PairAnagramViewProps {
  data: Record<string, unknown>;
  profile: string;
}

function groupHitsByLanguage(hits: AnagramHit[]): LanguageGroup[] {
  const map = new Map<string, AnagramHit[]>();
  const order: string[] = [];
  for (const hit of hits) {
    const lang = hit.language || "random";
    if (!map.has(lang)) {
      map.set(lang, []);
      order.push(lang);
    }
    map.get(lang)!.push(hit);
  }
  return order.map((language) => ({ language, hits: map.get(language)! }));
}

export function PairAnagramView({ data, profile }: PairAnagramViewProps) {
  const hits = (data.hits ?? []) as AnagramHit[];
  const hitCount = Number(data.hit_count ?? hits.length);
  const truncated = Boolean(data.truncated);
  const limit = 100;
  const languageGroups = useMemo(() => groupHitsByLanguage(hits), [hits]);

  return (
    <>
      <p className="gpm-metric__hint">{t("wortpaar.anagramDbNote")}</p>
      <div style={{ marginTop: "1rem", maxWidth: "28rem" }}>
        <PairWordCard
          original={String(data.query ?? "")}
          normalized={String(data.normalized ?? "")}
          substance={Number(data.substance ?? 0)}
          permIndex={Number(data.perm_index ?? 0)}
          actions={
            <QueryActions
              profile={profile}
              original={String(data.query ?? "")}
              normalized={String(data.normalized ?? "")}
              substance={Number(data.substance ?? 0)}
              permIndex={Number(data.perm_index ?? 0)}
              contentHash={String(data.content_hash ?? "") || undefined}
            />
          }
        />
      </div>
      <p className="gpm-metric__hint" style={{ marginTop: "1rem" }}>
        {hitCount > 0
          ? t("wortpaar.anagramHits").replace("{count}", String(hitCount))
          : t("wortpaar.anagramNoHits")}
        {truncated ? ` ${t("wortpaar.anagramTruncated").replace("{limit}", String(limit))}` : ""}
      </p>
      {languageGroups.length > 0 ? (
        <div className="gpm-anagram-lang-stack" style={{ marginTop: "0.75rem" }}>
          {languageGroups.map((group, index) => (
            <details key={group.language} className="gpm-anagram-lang" open={index === 0}>
              <summary>
                {t("wortpaar.anagramLanguageGroup")
                  .replace("{language}", languageLabel(group.language))
                  .replace("{count}", String(group.hits.length))}
              </summary>
              <div className="gpm-anagram-lang__panel">
                <div className="gpm-table-wrap">
                  <table className="gpm-table">
                    <thead>
                      <tr>
                        <th>{t("wortpaar.tables.original")}</th>
                        <th>{t("wortpaar.tables.normalized")}</th>
                        <th>{t("wortpaar.tables.index")}</th>
                        <th />
                      </tr>
                    </thead>
                    <tbody>
                      {group.hits.map((hit) => (
                        <AnagramHitRow
                          key={`${group.language}-${hit.word_normalized}-${hit.perm_index}`}
                          hit={hit}
                        />
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </details>
          ))}
        </div>
      ) : null}
    </>
  );
}

function QueryActions({
  profile,
  original,
  normalized,
  substance,
  permIndex,
  contentHash,
}: {
  profile: string;
  original: string;
  normalized: string;
  substance: number;
  permIndex: number;
  contentHash?: string;
}) {
  const navigate = useNavigate();
  const size = useSizeCompare();

  return (
    <div className="gpm-pair-actions">
      <div className="gpm-panel-actions">
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            saveDecodeDraft(substance, permIndex);
            navigate("/codec/decodieren");
          }}
        >
          {t("result.actions.copySi")}
        </Button>
        {contentHash ? (
          <Button
            type="button"
            variant="secondary"
            disabled={size.loading}
            onClick={() =>
              void size.run(() =>
                fetchSizeEncodeWord(contentHash, profile, {
                  original,
                  normalized,
                  substance,
                  perm_index: permIndex,
                }),
              )
            }
          >
            {size.loading ? t("result.actions.sizeLoading") : t("result.actions.sizeWord")}
          </Button>
        ) : null}
      </div>
      <SizeComparePanel data={size.data} loading={size.loading} error={size.error} />
    </div>
  );
}

function AnagramHitRow({ hit }: { hit: AnagramHit }) {
  const navigate = useNavigate();

  return (
    <tr>
      <td>{hit.word_original}</td>
      <td className="gpm-pair-word__norm">{hit.word_normalized}</td>
      <td className="mono">{formatBigInt(hit.perm_index)}</td>
      <td>
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            saveDecodeDraft(hit.substance, hit.perm_index);
            navigate("/codec/decodieren");
          }}
        >
          {t("result.actions.copySi")}
        </Button>
      </td>
    </tr>
  );
}
