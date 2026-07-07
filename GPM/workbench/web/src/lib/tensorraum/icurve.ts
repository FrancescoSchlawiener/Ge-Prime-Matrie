import type { SequenceItem } from "./types";

const lnFactCache = [0, 0];

export function lnFactorial(n: number): number {
  for (let i = lnFactCache.length; i <= n; i++) {
    lnFactCache.push(lnFactCache[i - 1] + Math.log(i));
  }
  return lnFactCache[n];
}

export function computeLnNI(items: SequenceItem[]): number {
  const counts = new Map<string, number>();
  for (const item of items) {
    const val = ("p" in item && item.p ? item.p : item.t) as string;
    counts.set(val, (counts.get(val) ?? 0) + 1);
  }
  let lnN = lnFactorial(items.length);
  counts.forEach((k) => {
    lnN -= lnFactorial(k);
  });
  return lnN;
}

export function formatNI(lnN: number): string {
  if (!Number.isFinite(lnN) || lnN <= 0) return "1";
  const exp10 = lnN / Math.LN10;
  if (exp10 < 6) return Math.round(Math.exp(lnN)).toLocaleString("de-DE");
  return `10^${exp10.toFixed(2)}`;
}

export function pointerNumericValue(pointerId: string): number {
  const idx = pointerId.lastIndexOf("_");
  if (idx === -1) return 0;
  const n = Number(pointerId.slice(idx + 1));
  return Number.isFinite(n) ? n : 0;
}

export function computeICurve(items: SequenceItem[]): number[] {
  const points: number[] = [];
  if (!items.length) return points;

  const counts = new Map<string, number>();
  let lnFactSum = 0;
  let prevVal = 0;

  for (let t = 0; t < items.length; t++) {
    const item = items[t];
    const val = ("p" in item && item.p ? item.p : item.t) as string;
    const numVal = pointerNumericValue(val);
    const c = counts.get(val) ?? 0;
    lnFactSum += Math.log(c + 1);
    counts.set(val, c + 1);

    const lnNCurrent = lnFactorial(t + 1) - lnFactSum;

    if (t === 0) {
      points.push(0);
    } else {
      const jump = Math.abs(numVal - prevVal);
      const lnJump = Math.log(Math.max(jump, 1));
      const denom = lnNCurrent > 0.0001 ? lnNCurrent : 0.0001;
      points.push(lnJump / denom);
    }
    prevVal = numVal;
  }

  return points;
}

export interface ICurvePoint {
  position: number;
  i_ratio: number;
}

export function toICurvePoints(values: number[]): ICurvePoint[] {
  return values.map((i_ratio, position) => ({ position, i_ratio }));
}
