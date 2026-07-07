import { SegmentToggle } from "../../../components/ui/SegmentToggle";
import { t } from "../../../i18n/t";
import type { TensorraumView } from "../../../lib/tensorraum";

const VIEWS: TensorraumView[] = ["workspace", "registry", "redundancy", "reversibility", "storage"];

interface TensorraumTabNavProps {
  view: TensorraumView;
  onViewChange: (view: TensorraumView) => void;
}

export function TensorraumTabNav({ view, onViewChange }: TensorraumTabNavProps) {
  return (
    <div className="gpm-tensor-tabnav">
      <SegmentToggle
        name="tensorraum-view"
        value={view}
        aria-label={t("tensorraum.tabs.aria")}
        options={VIEWS.map((key) => ({
          value: key,
          label: t(`tensorraum.tabs.${key}`),
          testId: key === "registry" ? "tensorraum-tab-registry" : undefined,
        }))}
        onChange={onViewChange}
      />
    </div>
  );
}
