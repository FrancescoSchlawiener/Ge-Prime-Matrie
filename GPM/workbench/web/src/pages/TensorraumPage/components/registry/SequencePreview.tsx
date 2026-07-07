import { useMemo } from "react";
import { t } from "../../../../i18n/t";
import { resolveSequencePreview, type RegistryMaps, type SequenceItem } from "../../../../lib/tensorraum";

interface SequencePreviewProps {
  sequence: SequenceItem[];
  registry: RegistryMaps;
  limit?: number;
}

export function SequencePreview({ sequence, registry, limit = 32 }: SequencePreviewProps) {
  const tokens = useMemo(
    () => resolveSequencePreview(sequence, registry, limit),
    [sequence, registry, limit],
  );

  if (!tokens.length) return null;

  return (
    <div className="gpm-tensor-sequence-preview">
      <span className="gpm-tensor-sequence-preview__label">{t("tensorraum.registry.sequencePreview")}</span>
      <div className="gpm-tensor-sequence-preview__tokens">
        {tokens.map((token, i) => (
          <span
            key={`${token.label}_${i}`}
            className={`gpm-tensor-sequence-preview__token gpm-tensor-sequence-preview__token--${token.kind}${
              token.type ? ` gpm-tensor-ptr--${token.type.toLowerCase()}` : ""
            }`}
            title={token.pointerFull}
          >
            {token.label}
          </span>
        ))}
        {sequence.length > tokens.length ? (
          <span className="gpm-tensor-sequence-preview__more">…</span>
        ) : null}
      </div>
    </div>
  );
}
