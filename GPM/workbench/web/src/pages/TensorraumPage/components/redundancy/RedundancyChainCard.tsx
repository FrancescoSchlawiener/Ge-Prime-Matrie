import { t } from "../../../../i18n/t";
import { resolvePointer, shortPointerId, type BlockChain, type RegistryMaps, type SentenceChain, type SequenceItem } from "../../../../lib/tensorraum";
import { PointerChip } from "../PointerChip";
import { ResonanceSparkline } from "./ResonanceSparkline";

function SequenceChips({ sequence, registry }: { sequence: SequenceItem[]; registry: RegistryMaps }) {
  return (
    <div className="gpm-tensor-resonance-card__chips">
      {sequence.map((item, idx) => {
        if (item.t === "S" || item.t === "N" || item.t === "D" || item.t === "C") {
          const label = resolvePointer(registry, item.t, item.p);
          return (
            <PointerChip key={`${idx}-${item.p}`} type={item.t} label={label} title={item.p} />
          );
        }
        const label = "p" in item ? item.p : item.t;
        return (
          <span key={`${idx}-${label}`} className="gpm-tensor-registry-mini">
            {item.t}:{shortPointerId(String(label))}
          </span>
        );
      })}
    </div>
  );
}

interface RedundancyChainCardProps {
  rank: number;
  mode: "block" | "sentence";
  chain: BlockChain | SentenceChain;
  registry: RegistryMaps;
}

export function RedundancyChainCard({ rank, mode, chain, registry }: RedundancyChainCardProps) {
  const sample = chain.occurrences[0];
  const sequence = sample.sequence;

  return (
    <article className="gpm-tensor-resonance-card">
      <header className="gpm-tensor-resonance-card__head">
        <div>
          <span className="gpm-tensor-resonance-card__rank">
            {t("tensorraum.redundancy.card.rank", { rank: String(rank) })}
          </span>
          <strong>{t("tensorraum.redundancy.card.occurrences", { count: String(chain.occurrences.length) })}</strong>
          <span className="gpm-tensor-resonance-card__meta">
            {t("tensorraum.redundancy.card.chainLength", { count: String(chain.chainLength) })}
            {mode === "sentence" && "windowSize" in chain ? (
              <> · {t("tensorraum.redundancy.card.windowSize", { size: String(chain.windowSize) })}</>
            ) : null}
          </span>
        </div>
        <code className="gpm-tensor-resonance-card__hash" title={t("tensorraum.redundancy.card.signature")}>
          {chain.hash.slice(0, 24)}…
        </code>
      </header>

      <ResonanceSparkline sequence={sequence} />

      <div className="gpm-tensor-resonance-card__locations">
        <h5>{t("tensorraum.redundancy.card.locations")}</h5>
        <ul>
          {chain.occurrences.slice(0, 6).map((occ, idx) => (
            <li key={`${occ.file}-${idx}`}>
              {mode === "block" && "node" in occ
                ? t("tensorraum.redundancy.card.locationBlock", {
                    file: occ.file,
                    nodeId: occ.node.id,
                  })
                : t("tensorraum.redundancy.card.locationSentence", {
                    file: occ.file,
                    start: String("start" in occ ? occ.start : 0),
                    size: String("windowSize" in occ ? occ.windowSize : chain.chainLength),
                  })}
            </li>
          ))}
          {chain.occurrences.length > 6 ? (
            <li className="gpm-metric__hint">
              +{chain.occurrences.length - 6}
            </li>
          ) : null}
        </ul>
      </div>

      <SequenceChips sequence={sequence.slice(0, 24)} registry={registry} />
      {sequence.length > 24 ? (
        <p className="gpm-metric__hint">+{sequence.length - 24} Token</p>
      ) : null}
    </article>
  );
}
