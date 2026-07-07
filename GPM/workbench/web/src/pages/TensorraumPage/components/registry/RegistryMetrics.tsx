import { t } from "../../../../i18n/t";
import { getRegistryOverview, type TensorraumProject } from "../../../../lib/tensorraum";

interface RegistryMetricsProps {
  project: TensorraumProject;
}

export function RegistryMetrics({ project }: RegistryMetricsProps) {
  const overview = getRegistryOverview(project);
  const items = [
    { key: "files", value: overview.files },
    { key: "spaces", value: overview.spaces },
    { key: "pointers", value: overview.total },
    { key: "languages", value: `${overview.languages}/${overview.languageTotal}` },
  ] as const;

  return (
    <div className="gpm-tensor-registry-metrics">
      {items.map((item) => (
        <div key={item.key} className="gpm-tensor-registry-metric">
          <span>{t(`tensorraum.registry.metrics.${item.key}`)}</span>
          <b>{item.value}</b>
        </div>
      ))}
    </div>
  );
}
