import { t } from "../../../i18n/t";
import type { PointerType } from "../../../lib/tensorraum";

const CLASS: Record<PointerType, string> = {
  S: "gpm-tensor-ptr gpm-tensor-ptr--s",
  N: "gpm-tensor-ptr gpm-tensor-ptr--n",
  D: "gpm-tensor-ptr gpm-tensor-ptr--d",
  C: "gpm-tensor-ptr gpm-tensor-ptr--c",
  H: "gpm-tensor-ptr gpm-tensor-ptr--h",
};

interface PointerChipProps {
  type: PointerType;
  label: string;
  title?: string;
}

export function PointerChip({ type, label, title }: PointerChipProps) {
  return (
    <span className={CLASS[type]} title={title ?? t(`tensorraum.pointers.${type}`)}>
      {label}
    </span>
  );
}
