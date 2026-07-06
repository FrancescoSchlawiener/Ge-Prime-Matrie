import { useCallback, useEffect, useMemo, useRef } from "react";
import type { SpectroMatch } from "../../../lib/ikurve/spectro";
import { mergeClassRanges } from "../../../lib/ikurve/spectro";
import { t } from "../../../i18n/t";

export interface ViewportPayload {
  reconstructed_text?: string;
  token_char_map?: Array<{
    token_index?: number;
    char_start?: number;
    char_end?: number;
  }>;
}

export interface TokenSelection {
  token_start: number;
  token_count: number;
}

interface GeometricMatrixProps {
  viewport: ViewportPayload | null | undefined;
  matches?: SpectroMatch[];
  label: string;
  onSelection?: (sel: TokenSelection | null) => void;
}

function buildCharTokenMap(
  text: string,
  tokenCharMap: ViewportPayload["token_char_map"],
): number[] {
  const map = new Array<number>(text.length).fill(-1);
  for (const entry of tokenCharMap ?? []) {
    const start = entry.char_start ?? 0;
    const end = entry.char_end ?? start;
    const tokenIndex = entry.token_index ?? -1;
    for (let i = start; i < end && i < text.length; i += 1) {
      map[i] = tokenIndex;
    }
  }
  return map;
}

function cellFromNode(node: Node | null): HTMLElement | null {
  if (!node) return null;
  const el = node.nodeType === Node.TEXT_NODE ? node.parentElement : (node as HTMLElement);
  return el?.closest?.(".geo-cell") ?? null;
}

export function GeometricMatrix({ viewport, matches = [], label, onSelection }: GeometricMatrixProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const text = String(viewport?.reconstructed_text ?? "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  const charTokenMap = useMemo(
    () => buildCharTokenMap(text, viewport?.token_char_map),
    [text, viewport?.token_char_map],
  );
  const spectroClasses = useMemo(() => mergeClassRanges(text.length, matches), [text.length, matches]);

  const readSelection = useCallback(() => {
    const root = rootRef.current;
    const selection = window.getSelection();
    if (!root || !selection || selection.isCollapsed || !onSelection) return;

    const anchorEl = cellFromNode(selection.anchorNode);
    const focusEl = cellFromNode(selection.focusNode);
    if (!anchorEl || !focusEl || !root.contains(anchorEl) || !root.contains(focusEl)) {
      onSelection(null);
      return;
    }

    const startRaw = anchorEl.dataset.tokenIndex;
    const endRaw = focusEl.dataset.tokenIndex;
    if (startRaw == null || endRaw == null || startRaw === "" || endRaw === "") {
      onSelection(null);
      return;
    }

    const startIdx = parseInt(startRaw, 10);
    const endIdx = parseInt(endRaw, 10);
    if (Number.isNaN(startIdx) || Number.isNaN(endIdx)) {
      onSelection(null);
      return;
    }

    onSelection({
      token_start: Math.min(startIdx, endIdx),
      token_count: Math.abs(endIdx - startIdx) + 1,
    });
  }, [onSelection]);

  useEffect(() => {
    if (!onSelection) return;
    const root = rootRef.current;
    if (!root) return;

    let timer: ReturnType<typeof setTimeout> | null = null;
    const schedule = () => {
      if (timer) clearTimeout(timer);
      timer = setTimeout(readSelection, 300);
    };

    const onSelectionChange = () => {
      const sel = window.getSelection();
      if (!sel?.anchorNode || !root.contains(sel.anchorNode)) return;
      schedule();
    };

    root.addEventListener("mouseup", schedule);
    document.addEventListener("selectionchange", onSelectionChange);
    return () => {
      if (timer) clearTimeout(timer);
      root.removeEventListener("mouseup", schedule);
      document.removeEventListener("selectionchange", onSelectionChange);
    };
  }, [onSelection, readSelection]);

  if (!text) {
    return <p className="gpm-metric__hint">{t("ikurve.common.noValue")}</p>;
  }

  const lines = text.split("\n");
  let offset = 0;
  const rows = lines.map((line, lineIdx) => {
    const cells: React.ReactNode[] = [];
    let currentRun = "";
    let currentTokenIndex = -2;
    let currentCls = "";
    let runStartPos = -1;

    const flushRun = () => {
      if (!currentRun) return;
      cells.push(
        <span
          key={runStartPos}
          className={`geo-cell${currentCls ? ` ${currentCls}` : ""}`}
          data-token-index={currentTokenIndex >= 0 ? currentTokenIndex : undefined}
        >
          {currentRun}
        </span>,
      );
      currentRun = "";
    };

    for (let col = 0; col < line.length; col += 1) {
      const pos = offset + col;
      const ch = line[col]!;
      const tokenIndex = charTokenMap[pos] ?? -1;
      const cls = spectroClasses[pos] || "";

      if (tokenIndex !== currentTokenIndex || cls !== currentCls) {
        flushRun();
        currentTokenIndex = tokenIndex;
        currentCls = cls;
        runStartPos = pos;
      }
      currentRun += ch;
    }
    flushRun();

    offset += line.length + 1;
    return (
      <div key={lineIdx} className="geo-line" data-line={lineIdx}>
        {cells.length ? cells : <span className="geo-cell geo-empty">&nbsp;</span>}
      </div>
    );
  });

  return (
    <div
      ref={rootRef}
      className="gpm-geometric-matrix"
      aria-label={label}
      tabIndex={0}
    >
      {rows}
    </div>
  );
}
