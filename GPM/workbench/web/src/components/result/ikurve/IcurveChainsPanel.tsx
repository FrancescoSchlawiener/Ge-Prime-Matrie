import { t } from "../../../i18n/t";
import { curvePoints } from "../../../lib/ikurve/curves";
import type { IcurveMode, SemanticDepth, StructuralDepth } from "../../../lib/ikurve/curves";
import { SEMANTIC_DEPTH_CONFIG, STRUCTURAL_DEPTH_CONFIG } from "../../../lib/ikurve/curves";
import { buildCellRows, buildHierarchyRows, buildSubstRows, buildWordTokenRows } from "../../../lib/ikurve/chainRows";
import { ChainsDataTable } from "./ChainsDataTable";

interface IcurveChainsPanelProps {
  data: Record<string, unknown>;
  mode: IcurveMode;
  depth: SemanticDepth | StructuralDepth;
}

export function IcurveChainsPanel({ data, mode, depth }: IcurveChainsPanelProps) {
  if (mode === "semantic") {
    return <HierarchyChains data={data} depth={depth as SemanticDepth} />;
  }
  if (mode === "structural") {
    return <StructuralChains data={data} />;
  }

  return (
    <div className="gpm-ikurve-zone">
      <h4 className="gpm-ikurve-zone__title">{t("ikurve.chains.tokens")}</h4>
      <ChainsDataTable
        headers={[
          t("ikurve.chains.columns.pos"),
          t("ikurve.chains.columns.wordA"),
          t("ikurve.chains.columns.permIndex"),
          t("ikurve.chains.columns.permN"),
          t("ikurve.chains.columns.iRatio"),
          t("ikurve.chains.columns.deltaRatio"),
          t("ikurve.chains.columns.deltaIndex"),
          t("ikurve.chains.columns.wordB"),
          t("ikurve.chains.columns.permIndex"),
          t("ikurve.chains.columns.permN"),
          t("ikurve.chains.columns.iRatio"),
          t("ikurve.chains.columns.deltaRatio"),
          t("ikurve.chains.columns.deltaIndex"),
        ]}
        rows={buildWordTokenRows(data)}
      />
      <h4 className="gpm-ikurve-zone__title" style={{ marginTop: "1rem" }}>
        {t("ikurve.chains.substance")}
      </h4>
      <ChainsDataTable
        headers={[
          t("ikurve.chains.columns.pos"),
          t("ikurve.chains.columns.wordA"),
          t("ikurve.chains.columns.substance"),
          t("ikurve.chains.columns.ggt"),
          t("ikurve.chains.columns.kgv"),
          t("ikurve.chains.columns.ggtKgv"),
          t("ikurve.chains.columns.sRatio"),
          t("ikurve.chains.columns.wordB"),
          t("ikurve.chains.columns.substance"),
          t("ikurve.chains.columns.ggt"),
          t("ikurve.chains.columns.kgv"),
          t("ikurve.chains.columns.ggtKgv"),
          t("ikurve.chains.columns.sRatio"),
        ]}
        rows={buildSubstRows(data)}
      />
      <h4 className="gpm-ikurve-zone__title" style={{ marginTop: "1rem" }}>
        {t("ikurve.chains.cells")}
      </h4>
      <ChainsDataTable
        headers={[
          t("ikurve.chains.columns.pos"),
          t("ikurve.chains.columns.permIndexA"),
          t("ikurve.chains.columns.iRatioA"),
          t("ikurve.chains.columns.permIndexB"),
          t("ikurve.chains.columns.iRatioB"),
        ]}
        rows={buildCellRows(data)}
      />
    </div>
  );
}

function HierarchyChains({ data, depth }: { data: Record<string, unknown>; depth: SemanticDepth }) {
  const cfg = SEMANTIC_DEPTH_CONFIG[depth];
  const ptsA = curvePoints((data.semantic_a as Record<string, Record<string, unknown>>)?.[cfg.dataKey]);
  const ptsB = curvePoints((data.semantic_b as Record<string, Record<string, unknown>>)?.[cfg.dataKey]);
  const rows = buildHierarchyRows(ptsA, ptsB, cfg.ratioKey);
  return (
    <div className="gpm-ikurve-zone">
      <h4 className="gpm-ikurve-zone__title">
        {t("ikurve.chains.semantic")}{t("ikurve.common.separator")}{t(`ikurve.depth.${depth}`)}
      </h4>
      <HierarchyTable rows={rows} />
    </div>
  );
}

function StructuralChains({ data }: { data: Record<string, unknown> }) {
  const cfg = STRUCTURAL_DEPTH_CONFIG.line;
  const ptsA = curvePoints((data.structural_a as Record<string, Record<string, unknown>>)?.lines);
  const ptsB = curvePoints((data.structural_b as Record<string, Record<string, unknown>>)?.lines);
  const rows = buildHierarchyRows(ptsA, ptsB, cfg.ratioKey);
  return (
    <div className="gpm-ikurve-zone">
      <h4 className="gpm-ikurve-zone__title">{t("ikurve.chains.structural")}</h4>
      <HierarchyTable rows={rows} />
    </div>
  );
}

function HierarchyTable({ rows }: { rows: (string | number)[][] }) {
  return (
    <ChainsDataTable
      headers={[
        t("ikurve.chains.columns.pos"),
        t("ikurve.chains.columns.wordA"),
        t("ikurve.chains.columns.sLevel"),
        t("ikurve.chains.columns.permIndex"),
        t("ikurve.chains.columns.permN"),
        t("ikurve.chains.columns.iRatio"),
        t("ikurve.chains.columns.ggt"),
        t("ikurve.chains.columns.kgv"),
        t("ikurve.chains.columns.wordB"),
        t("ikurve.chains.columns.sLevel"),
        t("ikurve.chains.columns.permIndex"),
        t("ikurve.chains.columns.permN"),
        t("ikurve.chains.columns.iRatio"),
        t("ikurve.chains.columns.ggt"),
        t("ikurve.chains.columns.kgv"),
      ]}
      rows={rows}
    />
  );
}
