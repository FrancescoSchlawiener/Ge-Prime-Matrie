import { useState } from "react";
import { t } from "../../../../i18n/t";
import { formatRegistryRow, type PointerType } from "../../../../lib/tensorraum";

interface RegistryEntryRowProps {
  type: PointerType;
  pointerId: string;
  value: string;
  hSegments?: Array<{ tag: string; value: string }>;
  dRelation?: { whole: number; den_reduced: number; ggt: number; display: string };
  sSubstance?: { substance: string; permIndex: string };
  cSubstance?: { substance: string; permIndex: string };
  hSubstance?: { substance: string };
}

function pointerChecksum(pointerId: string): string {
  const idx = pointerId.indexOf("_");
  return idx >= 0 ? pointerId.slice(idx + 1) : pointerId;
}

export function RegistryEntryRow({
  type,
  pointerId,
  value,
  hSegments,
  dRelation,
  sSubstance,
  cSubstance,
  hSubstance,
}: RegistryEntryRowProps) {
  const [copied, setCopied] = useState(false);
  const displayValue =
    type === "D" && dRelation
      ? `${dRelation.display} (${dRelation.whole}:${dRelation.den_reduced}:${dRelation.ggt})`
      : value;
  const row = formatRegistryRow(type, pointerId, displayValue);

  // Einheitliche Primzahl-Geometrie-Zeile je Kategorie (Substanz · Index/Checksum).
  let geometry: string | null = null;
  if (type === "S" && sSubstance) {
    geometry = `S=${sSubstance.substance} · I=${sSubstance.permIndex}`;
  } else if (type === "C" && cSubstance) {
    geometry = `S=${cSubstance.substance} · I=${cSubstance.permIndex}`;
  } else if (type === "N") {
    geometry = `N_${pointerChecksum(pointerId)}`;
  } else if (type === "H" && hSubstance) {
    geometry = `S=${hSubstance.substance}`;
  }

  async function onCopyId() {
    try {
      await navigator.clipboard.writeText(row.pointerFull);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      /* ignore */
    }
  }

  return (
    <tr className="gpm-tensor-registry-row">
      <td className="gpm-tensor-registry-row__type">
        <span className={`gpm-tensor-ptr gpm-tensor-ptr--${type.toLowerCase()}`}>{type}</span>
      </td>
      <td className="gpm-tensor-registry-row__label">
        <div>{row.label}</div>
        {geometry ? <div className="gpm-metric__hint gpm-tensor-registry-row__geometry">{geometry}</div> : null}
        {type === "H" && hSegments && hSegments.length > 0 ? (
          <div className="gpm-tensor-registry-row__segments">
            {hSegments.map((seg, i) => (
              <span key={`${seg.tag}-${i}`} className={`gpm-tensor-ptr gpm-tensor-ptr--${seg.tag.toLowerCase()}`}>
                {seg.tag}:{seg.value}
              </span>
            ))}
          </div>
        ) : null}
      </td>
      <td className="gpm-tensor-registry-row__id">
        <button
          type="button"
          className="gpm-tensor-registry-row__id-btn"
          title={row.pointerFull}
          onClick={() => void onCopyId()}
        >
          {copied ? t("tensorraum.registry.copiedPointer") : row.pointerShort}
        </button>
      </td>
    </tr>
  );
}
